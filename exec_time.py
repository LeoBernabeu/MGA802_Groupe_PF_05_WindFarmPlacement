from WindFarmPlacement.WindFarmPlacement import WindFarmPlacement
from WindFarmPlacement.WindFarm.windmill import Windmill
from WindFarmPlacement.WindFarm.windfarm import WindFarm
from WindFarmPlacement.topography import ElevationData

import time
import matplotlib.pyplot as plt

if __name__ == '__main__':

    lon_min, lon_max = -123.5, -122.5
    lat_min, lat_max = 48, 49

    start_time = time.time()
    study_area = WindFarmPlacement(lon_min, lon_max, lat_min, lat_max, 20, 20)
    study_area.get_wind_history_data_full_threaded([2018], 30)
    print(time.time()-start_time)

    # Affichage des vitesses moyennes du vent
    plt.imshow(study_area.wind_history.wind_mean, extent=[lon_min, lon_max, lat_min, lat_max], aspect='auto')
    plt.colorbar()
    plt.title("Vitesse moyenne du vent (en m/s) 2018")
    plt.xlabel("Longitude (°)")
    plt.ylabel("Latitude (°)")
    plt.show()

    wind_farm = WindFarm(10 * 2e5)
    num_windmills = 9  # Nombre d'éoliennes (à définir par l'utilisateur)
    for i in range(9):
        wind_farm.add_windmill(Windmill(50, 45))

    area_of_interest, power_matrix = study_area.find_adapted_zone(wind_farm, width=0.02)

    # Affichage des puissances
    plt.imshow(power_matrix, extent=[lon_min, lon_max, lat_min, lat_max], aspect='auto')
    plt.colorbar()
    plt.title("Estimation puissance produite sur une année (en W)")
    plt.xlabel("Longitude (°)")
    plt.ylabel("Latitude (°)")
    plt.show()

    # Retreive elevation data and calculate score
    elevation_data = ElevationData(area_of_interest[0][1][0], area_of_interest[0][1][1], area_of_interest[0][0][0],
                                   area_of_interest[0][0][1], 10, 10)
    elevation_data.retrieve_elevation_data()
    elevation_data.calculate_flatness_score()

    # Store elevation data and score
    elevation_array = elevation_data.get_elevation_array()
    flatness_score = elevation_data.flatness_score

    # Plot elevation data
    elevation_data.plot_3d_surface_map()
    # Print results
    print(f"Flatness score = ", flatness_score)

    # Define the area of interest as a 2D numpy array

    # Placer les éoliennes dans la zone d'intérêt
    windmill_coordinates = wind_farm.place_windmills(area_of_interest[0])
    print("Localisation des éoliennes")
    print(windmill_coordinates)
