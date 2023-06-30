from WindFarmPlacement.windfarmplacement import WindFarmPlacement
from WindFarmPlacement.WindFarm.windmill import Windmill
from WindFarmPlacement.WindFarm.windfarm import WindFarm
from WindFarmPlacement.elevationdata import ElevationData
from WindFarmPlacement.utils import print_message_console

import numpy as np
import matplotlib.pyplot as plt
import yaml
import os

# Paramètres de test pour la Study Area qui sont pas mal, i.e : début de résultat avec temps de calcul assez court.

if __name__ == '__main__':

    print("Veuillez entrer le nom du fichier YAML à utiliser pour charger les paramètres d'entrées : ")
    YAML_filename = input()

    # Load parameters from YAML file
    with open(YAML_filename, 'r') as file:
        parameters = yaml.load(file, Loader=yaml.FullLoader)

    print_message_console("Parameters have been acquired successfully")

    # Reference file
    path_to_data = parameters['path_to_data']
    reference_file = parameters['reference_file']

    # Study area and data acquisition parameters definition
    lon_min = parameters['lon_min']  # Min longitude of our study region
    lon_max = parameters['lon_max']  # Max longitude of our study region
    lat_min = parameters['lat_min']  # Min latidute of our study region
    lat_max = parameters['lat_max']  # Max latidute of our study region
    precision_lon = int(parameters['precision_lon'])  # Number of points to study along the longitude of our study region
    precision_lat = int(parameters['precision_lat'])  # Number of points to study along the latitude of our study region

    """On définit la zone d'étude avec les paramètres précédents. On distingue deux cas, celui où l'utilisateur passe un
    chemin vers le dossier de données, et celui-ci où il n'a pas de précision et donc on considère qu'il utilise le
    dossier data présent à la racine du projet."""
    if path_to_data:
        study_area = WindFarmPlacement(lon_min, lon_max, lat_min, lat_max, precision_lat, precision_lon, path_to_data)
    else:
        study_area = WindFarmPlacement(lon_min, lon_max, lat_min, lat_max, precision_lat, precision_lon)

    study_alt = parameters['study_alt']  # Altitude at which we gather wind data in meters, can be either 10, 30 or 50
    study_years = parameters['study_years']  # List of years that we want to study
    activate_multi_process = parameters['activate_multi_process']  # Activate multi-thread processing to decrease calculation time

    """On effectue ensuite le traitement des données pour les années passées en paramètre. On distingue la encore
    plusieurs cas, selon que l'utilisateur a activé la totalité du parallélisme ou non, et aussi selon qu'il a fournit
    un fichier de référence pour les données différent de celui de Climate Weather Canada"""
    if activate_multi_process:
        # Parallélisme sur les années et sur les mois
        if reference_file:
            study_area.get_wind_history_data_full_threaded(study_years, study_alt, reference_file=reference_file)
        else:
            study_area.get_wind_history_data_full_threaded(study_years, study_alt)
    else:
        # Parallélisme sur les mois
        if reference_file:
            study_area.get_wind_history_data(study_years, study_alt, reference_file=reference_file)
        else:
            study_area.get_wind_history_data(study_years, study_alt)
    print_message_console("Wind history data has been gathered successfully")

    # Print and save average wind speed figure
    plt.imshow(study_area.wind_history.wind_mean, extent=[lon_min, lon_max, lat_min, lat_max], aspect='auto')
    plt.colorbar()
    years_str = ", ".join(str(year) for year in study_years)
    plt.title(f"Average wind speed (m/s) {years_str}")
    plt.xlabel("Longitude (°)")
    plt.ylabel("Latitude (°)")
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_name = "Average_wind_speed.png"
    figure_path = os.path.join(current_directory, "../figures", file_name)
    plt.savefig(figure_path)

    plt.show()

    # Wind farm turbine parameters
    target_power = parameters['target_power']  # Target power of the wind turbine farm in Watts
    num_windmills = parameters['num_windmills']  # Number of wind turbines in the farm
    turb_height = parameters['turb_height']  # Altitude of turbine in meters, for accurate results, should be equal to study_alt (either 10, 30 or 50)
    blade_length = parameters['blade_length']  # Length of turbine blades in meters
    cut_in_speed = parameters['cut_in_speed']  # Speed at which the turbine starts producing power
    cut_out_speed = parameters['cut_out_speed']  # Speed at which the turbine stops producing power
    turbine_spacing = parameters['turbine_spacing']  # Spacing of individual turbines in the farm, a spacing of 5 will space them by 5 times their turbine diameter
    
    # Create wind farm object and add wind turbines to the wind farm
    wind_farm = WindFarm(target_power)
    for i in range(num_windmills):
        # On crée les éoliennes du champ
        wind_farm.add_windmill(Windmill(turb_height, blade_length, cut_in_speed, cut_out_speed))

    """On peut si l'on souhaite ajouter d'autres éoliennes avec des paramètres différents.
    Par exemple : wind_farm.add_windmill(Windmill(turb_height, 30, 5))
    Le champ d'éolienne utilisera alors les éoliennes les plus grandes (et donc plus puissantes) pour déterminer
    les espacements."""

    print_message_console("Wind turbine farm has been created successfully")

    """L'utilisateur peut indiquer le nombre de parcelles convenables à lui retourner. Selon, la précision et du maillage
    et la puissance visé, de très nombreuses parcelles de la zone d'étude peuvent convenir. Pour éviter de perdre
    l'utilisateur avec un trop grand nombre de résultats, nous envoyons par défaut seulement les 5 meilleures zones.
    L'utilisateur peut en demander plus ou moins dans le fichier ed paramètres."""
    num_areas_interest = int(parameters['num_areas_interest'])


    # Calculate the power matrix produced by our wind farm within the study area and find an area of interest
    if num_areas_interest:
        areas_of_interest, power_matrix = study_area.find_adapted_zone(wind_farm, turbine_spacing, nb_area=num_areas_interest)
    else:
        # Si on utilise la valeur par défaut
        areas_of_interest, power_matrix = study_area.find_adapted_zone(wind_farm, turbine_spacing)
    print_message_console("Power matrix and areas of interests have been calculated successfully")

    # Print and save power estimation figure
    plt.imshow(power_matrix, extent=[lon_min, lon_max, lat_min, lat_max], aspect='auto')
    plt.colorbar()
    plt.title("Yearly power estimate (W)")
    plt.xlabel("Longitude (°)")
    plt.ylabel("Latitude (°)")
    file_name = "Power_estimate_yearly.png"
    figure_path = os.path.join(current_directory, "../figures", file_name)
    plt.savefig(figure_path)

    plt.show()

    # Elevation data
    precision_lon_elevation = int(parameters['precision_lon_elevation'])
    precision_lat_elevation = int(parameters['precision_lat_elevation'])

    # Retrieve elevation data for all areas of interest and calculate topography score
    print_message_console("About to retrieve topography from Open Elevation API, this might take a few minutes.")
    elevation_arrays = []
    flatness_scores = []
    for area in range(areas_of_interest.shape[0]):
        # Retreive elevation data and calculate score # add for to loop through all areas of intests
        elevation_data = ElevationData(areas_of_interest[area][1][0], areas_of_interest[area][1][1],
                                       areas_of_interest[area][0][0], areas_of_interest[area][0][1],
                                       precision_lon_elevation, precision_lat_elevation)
        elevation_data.retrieve_elevation_data()
        elevation_data.calculate_flatness_score()

        # Store elevation data and score
        elevation_arrays.append(elevation_data.get_elevation_array())
        flatness_scores.append(elevation_data.flatness_score)
        print(f"The elevation score for area of interest {area} is {flatness_scores[area]}")

        # Plot elevation data
        elevation_data.plot_3d_surface_map(area)

    # Keep the area of interest that has the largest flatness score
    print_message_console("Topography and flatness scores have been calculated successfully")

    # Find the area of intesrest with the max flatness score and show its flatness score and power output
    index_max_topo = np.argmax(flatness_scores)
    print(f"The area of interest with the best flatness score is area {index_max_topo} with a score of {flatness_scores[index_max_topo]}")
    # print("It's yearly power output estimate is W")

    # Placer les éoliennes dans la zone d'intérêt
    windmill_coordinates = wind_farm.place_windmills(areas_of_interest[index_max_topo], turbine_spacing)
    print("\nLocation of wind turbines in the parc [lat,lon]")
    print(windmill_coordinates)

    print("\nTotal power of this area of interest")
    grid = np.meshgrid(study_area.long_array, study_area.lat_array)
    print(wind_farm.total_precise_theorical_produced_power(study_area.wind_history.weibull_factors, grid))
