import numpy as np
import scipy as sp

from Wind.utils import interp_grid

days = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


class WindHistory:
    """Historique du vent (année ou mois)"""

    def __init__(self, lat_array, long_array, year=None):
        self.lat_array, self.long_array = lat_array, long_array
        self.grid = np.meshgrid(lat_array, long_array)
        size_x, size_y = len(lat_array), len(long_array)
        self.wind_mean = np.zeros((size_x, size_y))
        self.wind_histo = np.zeros((size_x, size_y, 30))
        self.year = year
        self.stations = []

    def __add__(self, other):
        new_wind_history = WindHistory(self.lat_array, self.long_array, self.year)
        new_wind_history.wind_mean = self.wind_mean + other.wind_mean
        new_wind_history.wind_histo = self.wind_histo + other.wind_histo
        return new_wind_history

    def __iadd__(self, other):
        return self + other

    def add_station(self, station):
        self.stations.append(station)

    def update_stats(self, wind_field):
        """Fonction qui met les statistiques sur les classes de vent à partir des données d'un champ de vent.

        :param wind_field : Un champ de vent
        :type wind_field :
        :return:
        :rtype:
        """

        size_x, size_y = np.shape(self.wind_histo)[:-1]
        for x in range(size_x):
            self.wind_histo[x, np.arange(size_y), wind_field.astype(int)[x, :]] += 1

    def compute_history_month(self, month):
        """Fonction qui calcule pour chaque couple de coordonnée (latitude, longitude), la moyenne du vent et les
        paramètres statistiques de la distribution de Weibull sur un mois donné.

        :param month : Le mois à étudier, sur lequel calculer la moyenne et les paramètres statistiques.
        Janvier = 1, Février = 2, ..., Décembre = 12.
        :type month : int
        :return:
        :rtype:
        """

        # Chargement des données du mois étudié chez les stations
        for station in self.stations:
            # Si la station à des données sur ce mois elle les charge
            if station.contains_wind_measurements_month(self.year, month):
                station.load_data(self.year, month)
            # Dans le cas contraire, on s'assure de ne pas garder d'anciennes données qui ne concernent pas ce mois.
            else:
                station.reset_data()

        counter_div = 0
        xx, yy = self.grid
        for time in range(24*days[month]):  # On multiplie par 24 pour les heures d'une journée

            # À chaque instant, on récupère toutes les données disponibles auprès des stations
            wind_values = np.array([[wind_value, station.lat, station.long] for station in self.stations
                                    if (wind_value := station.get_data_timestamp(time))])

            # On effectue l'interpolation du champ de vent, si on a au moins 2 données (reste faible)
            if len(wind_values) > 2:
                counter_div += 1
                wind_field = interp_grid(xx, yy, wind_values)
                self.update_stats(wind_field)
                self.wind_mean += wind_field
        if counter_div != 0:
            self.wind_mean = self.wind_mean/counter_div

    def compute_history_year(self):
        """Fonction qui calcule pour chaque couple de coordonnée (latitude, longitude), la moyenne du vent et les
        paramètres statistiques de la distribution de Weibull sur toute l'année.

        :return:
        :rtype:
        """

        for month in range(1, 13):
            self.compute_history_month(month)
        return

    def weibull(self):
        """Fonction qui approxime les facteurs de forme et d'échelle de la distribution de Weibull du vent pour chaque
        coordonnée. Pour cela on utilise la méthode de scipy weibull_min.fit().

        :return:
        :rtype:
        """

        size_x, size_y = np.shape(self.wind_histo)[:-1]
        weibull = np.zeros((size_x, size_y, 2))
        for x in range(size_x):
            for y in range(size_y):
                # On récupère les données de l'histogramme pour la cellule étudiée
                histogram = self.wind_histo[x, y]

                # Problème la méthode fit utilise les "données brutes" et pas un histogramme
                raw_data = np.array([k for k in range(len(histogram)) for i in range(int(histogram[k]))])

                # On effectue l'approximation des facteurs de forme et d'échelle
                shape, loc, scale = sp.stats.weibull_min.fit(raw_data, floc=0)

                # On les assigne dans la cellule correspondante
                weibull[x, y] = [shape, scale]

        return weibull
