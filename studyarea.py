import numpy as np
import pandas as pd

from station import Station
from windhistory import WindHistory

from Wind.utils import gather


class StudyArea:

    def __init__(self, lat_min, lat_max, long_min, long_max, nb_lat, nb_long):
        self.lat_array = np.linspace(lat_min, lat_max, nb_lat).round(3)
        self.long_array = np.linspace(long_min, long_max, nb_long).round(3)
        self.near_stations = self.find_near_stations(1)
        self.wind_history = WindHistory(self.lat_array, self.long_array)
        self.windmills = []

    def find_near_stations(self, radius, required_stations=100):
        """Fonction qui recherche les stations les plus proches de la zone d'étude à partir des données contenues dans
        le fichier d'inventaire de https://climate.weather.gc.ca. Le rayon de recherche autour de la zone d'étude est
        incrémenté jusqu'à trouver un minimum de 100 stations par défaut.

        :param radius :
        :type radius : int
        :param required_stations : Nombre minimum de stations à récupérer
        :type required_stations : int
        :return: La liste des stations présentes dans le rayon de recherche
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

    def get_wind_history_data(self, year):
        wind_history = WindHistory(self.lat_array, self.long_array, year)
        for station in self.near_stations:
            if station.contains_wind_measurements_year(year):
                wind_history.add_station(station)
        wind_history.compute_history_year()
        self.wind_history += wind_history

    def add_windmill(self, windmill):
        self.windmills.append(windmill)

    def find_adapted_zone(self, power_goal):
        """Fonction qui recherche les portions de la zone qui permettent d'atteindre l'objectif de puissance produite.

        :param power_goal:
        :type power_goal:
        :return:
        :rtype:
        """

        # On commence par calculer la puissance théorique pouvant être produite
        total_power = np.zeros((len(self.lat_array), len(self.long_array)))
        for windmill in self.windmills:
            total_power += windmill.theoretical_power(self.wind_history)

        # On filtre pour garder les coordonnées des puissances qui atteignent l'objectif
        clusters = gather(total_power > power_goal)

        # On convertit les coordonnées cartésiennes dans les latitudes et longitudes correspondantes
        for i in range(len(clusters)):
            cluster = np.array(clusters[i])
            clusters[i] = (self.lat_array[cluster[:, 0]], self.long_array[cluster[:, 1]])

        return total_power, clusters
