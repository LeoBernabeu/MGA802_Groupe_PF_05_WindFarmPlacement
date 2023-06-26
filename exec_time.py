from WindFarmPlacement.WindFarmPlacement import StudyArea
import time
import matplotlib.pyplot as plt

if __name__ == '__main__':

    lon_min, lon_max = -123.5, -122.5
    lat_min, lat_max = 48, 49

    start_time = time.time()
    study_area = StudyArea(lon_min, lon_max, lat_min, lat_max, 100, 100)
    study_area.get_wind_history_data([2018], 30)
    print(time.time()-start_time)

    # Affichage des vitesses moyennes du vent
    plt.imshow(study_area.wind_history.wind_mean, extent=[lon_min, lon_max, lat_min, lat_max], aspect='auto')
    plt.colorbar()
    plt.title("Vitesse moyenne du vent (en m/s) 2018")
    plt.xlabel("Longitude (°)")
    plt.ylabel("Latitude (°)")
    plt.show()
