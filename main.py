from WindFarmPlacement.WindFarmPlacement import WindFarmPlacement
from WindFarmPlacement.WindFarm.windmill import Windmill
from WindFarmPlacement.WindFarm.windfarm import WindFarm
from WindFarmPlacement.topography import ElevationData

import numpy as np
import matplotlib.pyplot as plt

# Paramètres de test pour la Study Area qui sont pas mal, i.e : début de résultat avec temps de calcul assez court.

lon_min, lon_max = -123.5, -122.5
lat_min, lat_max = 48, 49

study_area = WindFarmPlacement(lon_min, lon_max, lat_min, lat_max, 50, 50)
study_area.get_wind_history_data([2018], 30)

# Affichage des vitesses moyennes du vent
plt.imshow(study_area.wind_history.wind_mean, extent=[lon_min, lon_max, lat_min, lat_max], aspect='auto')
plt.colorbar()
plt.title("Vitesse moyenne du vent (en m/s) 2018")
plt.xlabel("Longitude (°)")
plt.ylabel("Latitude (°)")
plt.show()

wind_farm = WindFarm(10*2e5)
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
elevation_data = ElevationData(area_of_interest[0][1][0], area_of_interest[0][1][1], area_of_interest[0][0][0], area_of_interest[0][0][1], 10, 10)
elevation_data.retrieve_elevation_data()
elevation_data.calculate_flatness_score()

# Store elevation data and score
elevation_array = elevation_data.get_elevation_array()
flatness_score = elevation_data.flatness_score

# Plot elevation data
elevation_data.plot_3d_surface_map()
# Print results
print(f"Flatness score = ",flatness_score)


# Define the area of interest as a 2D numpy array

# Placer les éoliennes dans la zone d'intérêt
windmill_coordinates = wind_farm.place_windmills(area_of_interest[0])
print("Localisation des éoliennes")
print(windmill_coordinates)

# # Création de l'objet FlatZoneFinder
# elevation_data = study_area.topography.elevation_data
# flat_zone_finder = FlatZoneFinder(elevation_data)
#
# # Trouver les zones plates
# flat_zone_finder.find_flat_zones(lat_min, lat_max, lon_min, lon_max)
#
# # Vérifier la planéité des zones
# for zone in flat_zone_finder.flat_zones:
#     lat, lon = zone
#     if flat_zone_finder.is_flat_zone(lat, lon):
#         print(f"Zone plate : Latitude = {lat}, Longitude = {lon}")
#
# # Vérifier l'espacement des zones
# turbine_diam = windmill.diameter
# flat_zone_finder.check_spacing(lat_min, lat_max, lon_min, lon_max, num_windmills=5, turbine_diam=turbine_diam)
# for zone in flat_zone_finder.good_zones:
#     lat, lon = zone
#     print(f"Zone suffisamment grande : Latitude = {lat}, Longitude = {lon}")
#
# # Afficher les éoliennes sur le graphique 3D
# flat_zone_finder.plot_windmills_on_3d_map(num_windmills=5)
