import numpy as np
import scipy as sp

from WindFarmPlacement.utils import interp_grid, number_days_for_month


class WindHistory:
    """Historique du vent (année ou mois)"""

    def __init__(self, long_array, lat_array, stations=None, altitude=None):
        size_x, size_y = len(long_array), len(lat_array)
        self.grid = np.meshgrid(long_array, lat_array)
        self.wind_mean = np.zeros((size_x, size_y))
        self.wind_histogram = np.zeros((size_x, size_y, 40))
        self.altitude = altitude
        self.stations = stations

    def __add__(self, other):
        xx, yy = self.grid
        new_wind_history = WindHistory(xx[0], yy[:,0])
        if np.all(self.wind_mean == np.zeros_like(self.wind_mean)):
            new_wind_history.wind_mean = other.wind_mean
        else:
            new_wind_history.wind_mean = (self.wind_mean + other.wind_mean)/2
        new_wind_history.wind_histogram = self.wind_histogram + other.wind_histogram
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

    def compute_history_month(self, year, month):
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
            if station.contains_wind_measurements_month(year, month):
                station.load_data(year, month)
            # Dans le cas contraire, on s'assure de ne pas garder d'anciennes données qui ne concernent pas ce mois.
            else:
                station.reset_data()

        counter_div = 0
        xx, yy = self.grid
        for time in range(24*number_days_for_month(month)):  # On multiplie par 24 pour les heures d'une journée

            # À chaque instant, on récupère toutes les données disponibles auprès des stations
            wind_values = np.array([[wind_value, station.long, station.lat] for station in self.stations
                                    if (wind_value := station.get_wind_data_timestamp(time))])

            # Si on dispose d'au moins 4 valeurs de vent on effectue l'interpolation du champ.
            # (Arbitraire et reste très faible)
            if len(wind_values) > 4:
                counter_div += 1

                # Interpolation
                wind_field = interp_grid(xx, yy, wind_values)
                if self.altitude:
                    wind_field = self.estimate_wind_speed_for_altitude(wind_field)

                # Mise à jour des statistiques et de la moyenne
                self.update_stats(wind_field)
                self.wind_mean += wind_field

        if counter_div != 0:
            # Calcul du champ de vent moyen
            self.wind_mean = self.wind_mean/counter_div

    def compute_history_year(self, year):
        """Fonction qui calcule pour chaque couple de coordonnée (latitude, longitude), la moyenne du vent et les
        paramètres statistiques de la distribution de Weibull sur toute l'année.

        :return:
        :rtype:
        """
        print("Year : ", year)
        for month in range(1, 13):
            print("Month : ", month)
            self.compute_history_month(year, month)

    def estimate_wind_speed_for_altitude(self, wind):
        """Fonction qui estime la vitesse du vent à une altitude donnée en utilisant le profil vertical de la vitesse
        du vent
        """

        altitude_measures = 10  # Les capteurs des stations sont à 10 m du sol
        z = 0.03  # Longueur de rugosité
        estimate_factor = np.log(self.altitude/z)/np.log(altitude_measures/z)

        return wind*estimate_factor

    def update_stats(self, wind_field):
        """Fonction qui met à jour les statistiques sur les classes de vent à partir des données d'un champ de vent.

        :param wind_field : Une matrice 2D représentant un champ de vent
        :type wind_field : numpy.array
        :return:
        :rtype :
        """

        size_x, size_y = self.wind_mean.shape
        for x in range(size_x):
            self.wind_histogram[x, np.arange(size_y), wind_field.astype(int)[x, :]] += 1

    def get_fit_weibull_factors(self):
        """Fonction qui approxime les facteurs de forme et d'échelle de la distribution de Weibull du vent pour chaque
        coordonnée. Pour cela on utilise la méthode de scipy weibull_min.fit().

        :return: Retourne une matrice 2D contenant les facteurs de forme et d'échelle
        :rtype : numpy.array
        """

        size_x, size_y = self.wind_mean.shape
        weibull = np.zeros((size_x, size_y, 2))
        for x in range(size_x):
            for y in range(size_y):
                # On récupère les données de l'histogramme pour la cellule étudiée
                histogram = self.wind_histogram[x, y]

                # La méthode fit utilise des "données brutes" et pas un histogramme. On perd en précision, mais on gagne
                # en gestion de la mémoire.
                raw_data = np.array([k for k in range(len(histogram)) for i in range(int(histogram[k]))])

                # On effectue l'approximation des facteurs de forme et d'échelle
                shape, loc, scale = sp.stats.weibull_min.fit(raw_data, floc=0)

                # On les assigne dans la cellule correspondante
                weibull[x, y] = [shape, scale]

        return weibull

    def calculate_weibull_factors_with_moments(self, x, y):
        """Calculer les facteurs de weibull. À vectoriser plus tard"""

        raw_data = np.array([k for k in range(len(self.wind_histogram[x, y])) for i in range(int(self.wind_histogram[x, y, k]))])

        bins = np.arange(41)
        bins_centers = (bins[:-1] + bins[1:]) / 2
        n = len(self.wind_histogram[x, y])

        # Calcul du moment d'ordre 1 (moyenne)
        mean = np.sum(bins_centers * self.wind_histogram[x, y]) / n

        # Calcul du moment d'ordre 2 (variance)
        var = np.sum((bins_centers - mean) ** 2 * self.wind_histogram[x, y]) / n

        # Calcul du moment d'ordre 3 (assymétrie)
        skewness = np.sum(((bins_centers - mean) / np.sqrt(var)) ** 3 * self.wind_histogram[x, y]) / n

        # Calcul du moment d'ordre 4 (kurtosis ?)
        kurtosis = np.sum(((bins_centers - mean) / np.sqrt(var)) ** 4 * self.wind_histogram[x, y]) / n - 3

        # Calculer estimation du facteur de forme
        shape = (kurtosis+3) / (skewness**2)

        # Calculer estimation du facteur d'échelle
        scale = np.sqrt(var / ((shape - 1)*mean**2))

        return [shape, scale]

    def get_moment_weibull_factors(self):
        """Matrice de weibull"""

        size_x, size_y = self.wind_mean.shape

        weibull = np.zeros((size_x, size_y, 2))

        for x in range(size_x):
            for y in range(size_y):
                weibull[x, y] = self.calculate_weibull_factors_with_moments(x, y)

        return weibull
