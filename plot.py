from WindFarmPlacement.WindFarmPlacement import StudyArea
import matplotlib.pyplot as plt
import scipy as sp
import numpy as np

# Paramètres de test pour la Study Area qui sont pas mal, i.e : début de résultat avec temps de calcul assez court.

lon_min, lon_max = -123.10, -123.00
lat_min, lat_max = 48.75, 48.85

study_area = StudyArea(lon_min, lon_max, lat_min, lat_max, 20, 20)
study_area.get_wind_history_data(range(2023, 2024), 30)

# Affichage des vitesses moyennes du vent
plt.imshow(study_area.wind_history.wind_mean, extent=[lon_min, lon_max, lat_min, lat_max], aspect='auto')
plt.colorbar()
plt.title("Vitesse moyenne du vent (en m/s) 2013-2023")
plt.xlabel("Longitude (°)")
plt.ylabel("Latitude (°)")
plt.show()
Weibull = study_area.wind_history.get_moment_weibull_factors()

histogram = study_area.wind_history.wind_histogram[12, 5]
normed_histogram = histogram/np.sum(histogram)
print(histogram)
print(np.sum(histogram))

x = np.arange(0, 40)

shape_atlas, scale_atlas = 1.66, 6.39
weibull_dist_atlas = sp.stats.weibull_min(shape_atlas, scale=scale_atlas)
pdf_atlas = weibull_dist_atlas.pdf(x)

shape_fit, scale_fit = 1.32, 4.22
weibull_dist_fit = sp.stats.weibull_min(shape_fit, scale=scale_fit)
pdf_fit = weibull_dist_fit.pdf(x)

shape, scale = Weibull[12, 5]
print(shape, scale)
weibull_dist = sp.stats.weibull_min(shape, scale=scale)
pdf = weibull_dist.pdf(x)

plt.figure()
plt.plot(x, pdf_atlas, 'r', label='Weibull atlas')
plt.plot(x, pdf_fit, 'b', label='Weibull obtenue avec weibull_min.fit()')
plt.plot(x, pdf, label='Weibull par calcul des moments')
plt.plot(normed_histogram)
plt.xlabel("Vitesse du vent (m/s)")
plt.ylabel("PDF")
plt.title("Comparaison des PDF des distributions de Weibull")
plt.legend()
plt.grid()
plt.show()


"""
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
"""