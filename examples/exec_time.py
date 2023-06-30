from WindFarmPlacement.windfarmplacement import WindFarmPlacement

import time
import yaml

if __name__ == '__main__':

    YAML_filename = "exec_time.yaml"

    # Load parameters from YAML file
    with open(YAML_filename, 'r') as file:
        parameters = yaml.load(file, Loader=yaml.FullLoader)

    lon_min, lon_max = parameters['lon_min'], parameters['lon_max']
    lat_min, lat_max = parameters['lat_min'], parameters['lat_max']

    precision_lon = int(parameters['precision_lon'])
    precision_lat = int(parameters['precision_lat'])

    start_time = time.time()
    study_area = WindFarmPlacement(lon_min, lon_max, lat_min, lat_max, precision_lon, precision_lat)
    study_area.get_wind_history_data_full_threaded(parameters['study_years'], parameters['study_alt'])
    exec_time_full_threaded = time.time()-start_time
    print(f"Temps d'exécution processus années ET mois {exec_time_full_threaded}")

    start_time = time.time()
    study_area = WindFarmPlacement(lon_min, lon_max, lat_min, lat_max, precision_lon, precision_lat)
    study_area.get_wind_history_data(parameters['study_years'], parameters['study_alt'])
    exec_time_month_threaded = time.time()-start_time
    print(f"Temps d'exécution processus mois SEULEMENT {exec_time_month_threaded}")

    print(f"Rapport temps d'éxécution entre les deux méthodes {exec_time_month_threaded/exec_time_full_threaded}")
