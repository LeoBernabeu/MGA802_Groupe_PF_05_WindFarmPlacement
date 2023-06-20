import numpy as np
import pandas as pd
from math import ceil

from WindFarmPlacement.WeatherData import Station
from WindFarmPlacement.WeatherData import WindHistory

from WindFarmPlacement.utils import gather, rectangle


class StudyArea:

    def __init__(self, long_min, long_max, lat_min, lat_max, nb_lat, nb_long):
        self.long_array = np.linspace(long_min, long_max, nb_long).round(3)
        self.lat_array = np.linspace(lat_min, lat_max, nb_lat).round(3)
        self.wind_history = WindHistory(self.long_array, self.lat_array)

    def find_near_stations(self, radius, required_stations=100):
        """Fonction qui recherche les stations les plus proches de la zone d'étude à partir des données contenues dans
        le fichier d'inventaire de https://climate.weather.gc.ca. Le rayon de recherche autour de la zone d'étude est
        incrémenté jusqu'à trouver un minimum de 100 stations par défaut.

        :param radius : Rayon de recherche des stations autour de la zone d'étude.
        :type radius : int
        :param required_stations : Nombre minimum de stations à récupérer.
        :type required_stations : int
        :return: Retourne une liste des stations trouvées dans le rayon de recherche.
        :rtype : list[Station]
        """

        # Calcul des bornes de recherche sur la latitude et la longitude.
        lat_min, lat_max = self.lat_array[0] - radius, self.lat_array[-1] + radius
        long_min, long_max = self.long_array[0] - radius, self.long_array[-1] + radius

        # Création de la DataFrame avec les colonnes qui nous intéressent.
        df = pd.read_csv("Station_Inventory_EN.csv", usecols=(3, 6, 7, 10), skiprows=3)

        # Recherche des stations dont la latitude et la longitude sont compris dans l'intervalle de recherche.
        lat_index = np.array(df.index[df["Latitude (Decimal Degrees)"].between(lat_min, lat_max)])
        long_index = np.array(df.index[df["Longitude (Decimal Degrees)"].between(long_min, long_max)])
        good_index = np.intersect1d(lat_index, long_index)

        # Si le nombre de stations trouvées est insuffisant, on relance la recherche en augmentant le rayon.
        if len(good_index) < required_stations:
            stations = self.find_near_stations(radius+1)
        # Sinon, on crée une liste d'objets stations avec les données utiles.
        else:
            stations = []
            for index in good_index:
                station_id, lat, long, elev = df.iloc[index]
                stations.append(Station(int(station_id), lat, long, elev))
        return stations

    def get_wind_history_data(self, period, altitude):
        """Fonction qui récupère les données historiques de la zone d'étude pour une année donnée.

        :param year : L'année à étudier.
        :type year : int
        :return:
        :rtype:
        """

        near_stations = self.find_near_stations(1)

        for year in period:

            usefull_stations = []
            # On ajoute les stations proches de la zone d'étude qui possèdent des données sur cette année.
            for station in near_stations:
                if station.contains_wind_measurements_year(year):
                    usefull_stations.append(station)
            # On crée un nouveau WindHistory pour l'année d'étude
            wind_history = WindHistory(self.long_array, self.lat_array, usefull_stations, altitude)
            # On lance le calcul des données historiques.
            wind_history.compute_history_year(year)

            self.wind_history += wind_history

    def find_adapted_zone(self, windfarm, width=0.1, nb_area=5):
        """Fonction qui recherche les portions de la zone qui permettent d'atteindre l'objectif de puissance produite.

        :param power_goal : Production de puissance visée par le champ éolien
        :type power_goal : float
        :param width : Taille des zones. Si max_width = 0.1, alors on cherche un ensemble de coordonnées contiguës qui
        forme un rectangle de longueur 0.1 degré de latitude et de largeur 0.1 degré de longitude.
        :type width : float
        :param nb_area : Nombre de zones maximum à renvoyer.
        :type nb_area : int
        :return:
        :rtype :
        """

        # On commence par calculer les facteurs de la distribution de Weibull
        weibull_factors = self.wind_history.get_fit_weibull_factors()

        # On calcule ensuite la puissance théorique pouvant être produite
        total_power = windfarm.total_theoretical_produced_power(weibull_factors)

        # On filtre pour garder les coordonnées des puissances qui atteignent l'objectif et on regarde celles contiguës
        clusters = gather(total_power > windfarm.target_power)

        area_of_interest_coordinates = None
        # S'il y a des ensembles de cellules qui respectent l'objectif de puissance
        if clusters:
            # On calcule le nombre de cases dans un rectangle qui correspond à la taille des zones recherchées.
            width_lat = (self.lat_array[1] - self.lat_array[0]).round(3)
            width_long = (self.long_array[1] - self.long_array[0]).round(3)
            width_x, width_y = ceil(width / width_long), ceil(width / width_lat)

            # On cherche toutes les zones rectangulaires
            rectangular_areas = []
            for i in range(len(clusters)):
                rectangular_areas.extend(rectangle(clusters[i], width_x, width_y))

            if len(rectangular_areas) > nb_area:
                # On trie les rectangles selon la puissance théorique max et on ne garde que les meilleurs selon nb_area
                arg_sort = np.zeros(len(rectangular_areas))
                for i in range(len(rectangular_areas)):
                    start, end = rectangular_areas[i][0], rectangular_areas[i][1]
                    columns = rectangular_areas[i][2]
                    sub_power_matrix = total_power[start:end][:, columns]
                    arg_sort[i] = np.max(sub_power_matrix)
                sort_index = np.argsort(arg_sort)
                rectangular_areas = [rectangular_areas[sort_index[k]] for k in range(nb_area)]

            # Les rectangles sont sélectionnés, on renvoie à la place des couples de longitude et latitude
            area_of_interest_coordinates = np.zeros((len(rectangular_areas), 2, 2))
            columns = np.array([rectangular_areas[k][2] for k in range(len(rectangular_areas))])
            limits = np.array([np.arange(rectangular_areas[k][0], rectangular_areas[k][1])
                               for k in range(len(rectangular_areas))])
            latitudes = np.array(self.lat_array[limits])
            print("Latirudes : ", latitudes)
            lat_limits = [np.min(latitudes, axis=1)-width/2, np.max(latitudes, axis=1)+width/2]
            print(lat_limits)
            area_of_interest_coordinates[:, 0, 0] = lat_limits[0]
            area_of_interest_coordinates[:, 0, 1] = lat_limits[1]
            longitudes = np.array(self.long_array[columns])
            print("Longitudes : ", longitudes)
            lon_limits = [np.min(longitudes, axis=1)-width/2, np.max(longitudes, axis=1)+width/2]
            print(lon_limits)
            area_of_interest_coordinates[:, 1, 0] = lon_limits[0]
            area_of_interest_coordinates[:, 1, 1] = lon_limits[1]

        return area_of_interest_coordinates, total_power
