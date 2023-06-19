import numpy as np
import scipy as sp

from .utils import interp_grid, number_days_for_month


class WindHistory:
    """Historique du vent (année ou mois)"""

    def __init__(self, lat_array, long_array, year=None):
        self.lat_array, self.long_array = lat_array, long_array
        self.grid = np.meshgrid(lat_array, long_array)
        size_x, size_y = len(lat_array), len(long_array)
        self.wind_mean = np.zeros((size_x, size_y))
        self.wind_histo = np.zeros((size_x, size_y, 30))
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
        """Fonction qui ajoute une station à la liste de celles utilisées pour calculer l'historique sur les vents.

        :param station : Une station météorologique.
        :type station : Station
        :return:
        :rtype :
        """
        self.stations.append(station)

    def update_stats(self, wind_field):
        """Fonction qui met à jour les statistiques sur les classes de vent à partir des données d'un champ de vent.

        :param wind_field : Une matrice 2D représentant un champ de vent
        :type wind_field : numpy.array
        :return:
        :rtype :
        """

        size_x, size_y = len(self.lat_array), len(self.long_array)
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
        for time in range(24*number_days_for_month(month)):  # On multiplie par 24 pour les heures d'une journée

            # À chaque instant, on récupère toutes les données disponibles auprès des stations
            wind_values = np.array([[wind_value, station.lat, station.long] for station in self.stations
                                    if (wind_value := station.get_wind_data_timestamp(time))])

            # Si on dispose d'au moins 4 valeurs de vent on effectue l'interpolation du champ.
            # (Arbitraire et reste très faible)
            if len(wind_values) > 4:
                counter_div += 1

                # Interpolation
                wind_field = interp_grid(xx, yy, wind_values)

                # Mise à jour des statistiques et de la moyenne
                self.update_stats(wind_field)
                self.wind_mean += wind_field

        if counter_div != 0:
            # Calcul du champ de vent moyen
            self.wind_mean = self.wind_mean/counter_div

    def compute_history_year(self):
        """Fonction qui calcule pour chaque couple de coordonnée (latitude, longitude), la moyenne du vent et les
        paramètres statistiques de la distribution de Weibull sur toute l'année.

        :return:
        :rtype:
        """

        for month in range(1, 13):
            self.compute_history_month(month)

    def weibull(self):
        """Fonction qui approxime les facteurs de forme et d'échelle de la distribution de Weibull du vent pour chaque
        coordonnée. Pour cela on utilise la méthode de scipy weibull_min.fit().

        :return: Retourne une matrice 2D contenant les facteurs de forme et d'échelle
        :rtype : numpy.array
        """

        size_x, size_y = len(self.lat_array), len(self.long_array)
        weibull = np.zeros((size_x, size_y, 2))
        for x in range(size_x):
            for y in range(size_y):
                # On récupère les données de l'histogramme pour la cellule étudiée
                histogram = self.wind_histo[x, y]

                # La méthode fit utilise des "données brutes" et pas un histogramme. On perd en précision, mais on gagne
                # en gestion de la mémoire.
                raw_data = np.array([k for k in range(len(histogram)) for i in range(int(histogram[k]))])

                # On effectue l'approximation des facteurs de forme et d'échelle
                shape, loc, scale = sp.stats.weibull_min.fit(raw_data, floc=0)

                # On les assigne dans la cellule correspondante
                weibull[x, y] = [shape, scale]

        return weibull
