from WindFarm.studyarea import StudyArea
from WindFarm.Wind.windmill import Windmill
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
