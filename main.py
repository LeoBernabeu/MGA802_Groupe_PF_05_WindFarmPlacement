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

    # Reference file
    path_to_data = parameters['path_to_data']
    reference_file = parameters['reference_file']

    # Study area and data acquisition parameters definition
    lon_min = parameters['lon_min']                     # Min longitude of our study region
    lon_max = parameters['lon_max']                     # Max longitude of our study region
    lat_min = parameters['lat_min']                     # Min latidute of our study region
    lat_max = parameters['lat_max']                     # Max latidute of our study region
    precision_lon = int(parameters['precision_lon'])    # Number of points to study along the longitude of our study region
    precision_lat = int(parameters['precision_lat'])    # Number of points to study along the latitude of our study region
    study_alt = parameters['study_alt']                 # Altitude at which we gather wind data in meters, can be either 10, 30 or 50
    study_years = parameters['study_years']             # List of years that we want to study
    activate_multi_process = parameters['activate_multi_process']   # Activate multi-thread processing to decrease calculation time
    num_areas_interest = int(parameters['num_areas_interest'])      # Number of sub-areas of intesrests to further study within the study area

    # Elevation data
    precision_lon_elevation = int(parameters['precision_lon_elevation'])
    precision_lat_elevation = int(parameters['precision_lat_elevation'])

    # Wind farm turbine parameters
    target_power = parameters['target_power']   # Target power of the wind turbine farm in Watts
    num_windmills = parameters['num_windmills'] # Number of wind turbines in the farm
    turb_height = parameters['turb_height']     # Altitude of turbine in meters, for accurate results, should be equal to study_alt (either 10, 30 or 50)
    blade_length = parameters['blade_length']   # Length of turbine blades in meters
    cut_in_speed = parameters['cut_in_speed']   # Speed at which the turbine starts producing power
    cut_out_speed = parameters['cut_out_speed']  # Speed at which the turbine stops producing power
    turbine_spacing = parameters['turbine_spacing']  # Spacing of individual turbines in the farm, a spacing of 5 will space them by 5 times their turbine diameter
    print_message_console("Parameters have been acquired successfully")

    # Define study area and get wind history data
    if path_to_data:
        study_area = WindFarmPlacement(lon_min, lon_max, lat_min, lat_max, precision_lat, precision_lon, path_to_data)
    else:
        study_area = WindFarmPlacement(lon_min, lon_max, lat_min, lat_max, precision_lat, precision_lon)

    if activate_multi_process:
        if reference_file:
            study_area.get_wind_history_data_full_threaded(study_years, study_alt, reference_file=reference_file)
        else:
            study_area.get_wind_history_data_full_threaded(study_years, study_alt)
    else:
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
    figure_path = os.path.join(current_directory, "figures", file_name)
    plt.savefig(figure_path)

    plt.show()
    
    # Create wind farm object and add wind turbines to the wind farm
    wind_farm = WindFarm(target_power)
    for i in range(num_windmills):
        wind_farm.add_windmill(Windmill(turb_height, blade_length, cut_in_speed, cut_out_speed))
    print_message_console("Wind turbine farm has been created successfully")

    # Calculate the power matrix produced by our wind farm within the study area and find an area of interest
    areas_of_interest, power_matrix = study_area.find_adapted_zone(wind_farm, turbine_spacing, nb_area=num_areas_interest)
    print_message_console("Power matrix and areas of interests have been calculated successfully")

    # Print and save power estimation figure
    plt.imshow(power_matrix, extent=[lon_min, lon_max, lat_min, lat_max], aspect='auto')
    plt.colorbar()
    plt.title("Yearly power estimate (W)")
    plt.xlabel("Longitude (°)")
    plt.ylabel("Latitude (°)")
    file_name = "Power_estimate_yearly.png"
    figure_path = os.path.join(current_directory, "figures", file_name)
    plt.savefig(figure_path)

    plt.show()

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
