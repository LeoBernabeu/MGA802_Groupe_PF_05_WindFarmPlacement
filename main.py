from WindFarm.studyarea import StudyArea
from WindFarm.Wind.windmill import Windmill
import matplotlib.pyplot as plt

# Paramètres de test pour la Study Area qui sont pas mal, i.e : début de résultat avec temps de calcul assez court.

study_area = StudyArea(48, 49, -123.5, -122.5, 50, 50)
study_area.get_wind_history_data(2018)
plt.imshow(study_area.wind_history.wind_mean)
plt.colorbar()
plt.show()
windmill = Windmill(50, 45)
study_area.add_windmill(windmill)
power_matrix, cluster = study_area.find_adapted_zone(2e5, width=0.05)
print(cluster)
plt.imshow(power_matrix)
plt.colorbar()
plt.show()
