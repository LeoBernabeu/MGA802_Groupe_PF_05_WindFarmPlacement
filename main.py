from WindFarm.studyarea import StudyArea
from WindFarm.Wind.windmill import Windmill
from flat_zone_finder import FlatZoneFinder
import matplotlib.pyplot as plt

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


# Création de l'objet FlatZoneFinder
elevation_data = study_area.topography.elevation_data
flat_zone_finder = FlatZoneFinder(elevation_data)

# Trouver les zones plates
flat_zone_finder.find_flat_zones(lat_min, lat_max, lon_min, lon_max)

# Vérifier la planéité des zones
for zone in flat_zone_finder.flat_zones:
    lat, lon = zone
    if flat_zone_finder.is_flat_zone(lat, lon):
        print(f"Zone plate : Latitude = {lat}, Longitude = {lon}")

# Vérifier l'espacement des zones
turbine_diam = windmill.diameter
flat_zone_finder.check_spacing(lat_min, lat_max, lon_min, lon_max, num_windmills=5, turbine_diam=turbine_diam)
for zone in flat_zone_finder.good_zones:
    lat, lon = zone
    print(f"Zone suffisamment grande : Latitude = {lat}, Longitude = {lon}")

# Afficher les éoliennes sur le graphique 3D
flat_zone_finder.plot_windmills_on_3d_map(num_windmills=5)
