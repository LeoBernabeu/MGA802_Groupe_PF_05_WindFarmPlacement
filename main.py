from WindFarmPlacement.studyarea import StudyArea
from WindFarmPlacement.WindFarm.windmill import Windmill
#from flat_zone_finder import FlatZoneFinder
import numpy as np
import matplotlib.pyplot as plt

def place_windmills(area_of_interest, num_windmills):
    rotor_diameter = 50  # Diamètre du rotor d'une éolienne (en mètres)
    distance = 5 * rotor_diameter  # Distance d'espacement entre les éoliennes

    lat_min, lat_max = area_of_interest[0]
    lon_min, lon_max = area_of_interest[1]

    latitudes = []
    longitudes = []

    # Calcul du centre de la petite section
    lat_center = (lat_min + lat_max) / 2
    lon_center = (lon_min + lon_max) / 2

    # Placer une éolienne au centre de la petite section
    latitudes.append(lat_center)
    longitudes.append(lon_center)

    # Espacement des éoliennes autour de l'éolienne centrale
    angle = 2 * np.pi / num_windmills  # Angle entre chaque éolienne

    # Placer les éoliennes dans chaque petite section
    for i in range(1, num_windmills + 1):
        # Calcul des coordonnées polaires pour chaque éolienne
        lat_offset = np.sin(i * angle) * (distance / 111000)  # Conversion en latitude (~111000 mètres par degré)
        lon_offset = np.cos(i * angle) * (distance / (111000 * np.cos(np.radians(lat_center))))  # Conversion en longitude (~111000 mètres par degré, ajusté par la latitude)

        # Calcul des nouvelles latitudes et longitudes
        new_latitude = lat_center + lat_offset
        new_longitude = lon_center + lon_offset

        latitudes.append(new_latitude)
        longitudes.append(new_longitude)

    # Convertir les listes de latitudes et longitudes en un tableau numpy
    windmill_coordinates = np.vstack((latitudes, longitudes)).T

    # Display windmill locations on a 2D plot
    plt.scatter(windmill_coordinates[:, 1], windmill_coordinates[:, 0], color='red', marker='x')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Localisation de chaque éoliennes dans le parc éolien')
    plt.show()

    return windmill_coordinates

# Paramètres de test pour la Study Area qui sont pas mal, i.e : début de résultat avec temps de calcul assez court.

lon_min, lon_max = -123.5, -122.5
lat_min, lat_max = 48, 49

study_area = StudyArea(lon_min, lon_max, lat_min, lat_max, 50, 50)
study_area.get_wind_history_data(2018)

# Affichage des vitesses moyennes du vent
plt.imshow(study_area.wind_history.wind_mean, extent=[lon_min, lon_max, lat_min, lat_max], aspect='auto')
plt.colorbar()
plt.title("Vitesse moyenne du vent (en m/s) 2018")
plt.show()

windmill = Windmill(50, 45)
study_area.add_windmill(windmill)
power_matrix = study_area.windfarm_theoric_power()

# Affichage des puissances
plt.imshow(power_matrix, extent=[lon_min, lon_max, lat_min, lat_max], aspect='auto')
plt.colorbar()
plt.title("Estimation puissance produite sur une année (en W)")
plt.show()

area_of_interest = study_area.find_adapted_zone(2e5, width=0.05)
print(area_of_interest)

# Define the area of interest as a 2D numpy array
area_of_interest = np.array([[lat_min, lat_max], [lon_min, lon_max]])

# Placer les éoliennes dans la zone d'intérêt
num_windmills = 10  # Nombre d'éoliennes (à définir par l'utilisateur)
windmill_coordinates = place_windmills(area_of_interest, num_windmills)

# Get the windmill coordinates
print("Localisation des éoliennes:")
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
