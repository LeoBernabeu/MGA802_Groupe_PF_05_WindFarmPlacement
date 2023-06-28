import numpy as np
import scipy as sp

import logging
import multiprocessing

from WindFarmPlacement.WeatherData.fasthistoryyearprocess import FastHistoryYearProcess
from WindFarmPlacement.WeatherData.fasthistorymonthprocess import FastHistoryMonthProcess


class WindHistory:
    """Initialise un objet WindHistory pour l'historique du vent (année ou mois).

    :param long_array: Un tableau de longitudes.
    :type long_array: numpy.array
    :param lat_array: Un tableau de latitudes.
    :type lat_array: numpy.array
    :param stations: Une liste des stations météorologiques, par défaut None.
    :type stations: list, optional
    :param altitude: L'altitude, par défaut None.
    :type altitude: float, optional
    """

    def __init__(self, long_array, lat_array, stations=None, altitude=None):
        size_x, size_y = len(long_array), len(lat_array)
        self.grid = np.meshgrid(long_array, lat_array)
        self.wind_mean = np.zeros((size_x, size_y))
        self.wind_histogram = np.zeros((size_x, size_y, 40))
        self.altitude = altitude
        self.stations = stations

    def __add__(self, other):
        """Surcharge de l'opérateur d'addition (+).

        :param other: Un autre objet WindHistory.
        :type other: WindHistory
        :return: Un nouvel objet WindHistory résultant de l'addition.
        :rtype: WindHistory
        """

        xx, yy = self.grid
        new_wind_history = WindHistory(xx[0], yy[:, 0])
        if np.all(self.wind_mean == np.zeros_like(self.wind_mean)):
            new_wind_history.wind_mean = other.wind_mean
        else:
            new_wind_history.wind_mean = (self.wind_mean + other.wind_mean)/2
        new_wind_history.wind_histogram = self.wind_histogram + other.wind_histogram
        return new_wind_history

    def __iadd__(self, other):
        """Surcharge de l'opérateur d'addition et d'affectation (+=).

        :param other: Un autre objet WindHistory.
        :type other: WindHistory
        :return: L'objet WindHistory actuel après l'addition.
        :rtype: WindHistory
        """

        return self + other

    def add_station(self, station):
        """Fonction qui ajoute une station à la liste de celles utilisées pour calculer l'historique sur les vents.

        :param station: Une station météorologique.
        :type station: Station
        """

        self.stations.append(station)

    def compute_history_year(self, year):
        """Fonction qui calcule pour chaque couple de coordonnée (latitude, longitude), la moyenne du vent et les
        paramètres statistiques de la distribution de Weibull sur toute l'année.

        :param year: Année.
        :type year: int
        """

        logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )

        print("Year : ", year)

        follow_threads = []
        for month in range(1, 13):
            # Chargement des données du mois étudié chez les stations
            for station in self.stations:
                # Si la station à des données sur ce mois elle les charge
                if station.contains_wind_measurements_month(year, month):
                    station.load_data(year, month)
                # Dans le cas contraire, on s'assure de ne pas garder d'anciennes données qui ne concernent pas ce mois.
                else:
                    station.reset_data(month)

            logging.debug(f'Data loaded')

            threaded_q = multiprocessing.Queue()
            threaded_interpolation = FastHistoryMonthProcess(self.grid, self.stations, year, month, self.altitude,
                                                             threaded_q)
            follow_threads.append((threaded_interpolation, threaded_q))

        for thread in follow_threads:
            thread[0].start()

        count_div = 0
        for thread_and_queue in follow_threads:
            wind_mean, wind_histo = thread_and_queue[1].get()
            thread_and_queue[0].join()
            self.wind_mean += wind_mean
            self.wind_histogram += wind_histo
            count_div += 1

        self.wind_mean = self.wind_mean/count_div

    def compute_history(self, period):
        """Fonction qui calcule l'historique du vent pour une période donnée.

        :param period: Période.
        :type period: list
        """

        follow_threads = []
        for year in period:
            threaded_q = multiprocessing.Queue()
            thread = FastHistoryYearProcess(self.grid, self.stations, year, self.altitude, threaded_q)
            follow_threads.append((thread, threaded_q))

        for thread in follow_threads:
            thread[0].start()

        for thread_and_queue in follow_threads:
            wind_year_mean, wind_year_histogram = thread_and_queue[1].get()
            thread_and_queue[0].join()
            self.wind_mean += wind_year_mean
            self.wind_histogram += wind_year_histogram

        self.wind_mean = self.wind_mean/len(period)

    def get_fit_weibull_factors(self):
        """Fonction qui approxime les facteurs de forme et d'échelle de la distribution de Weibull du vent pour chaque
        coordonnée. Pour cela on utilise la méthode de scipy weibull_min.fit().

        :return: Retourne une matrice 2D contenant les facteurs de forme et d'échelle
        :rtype: numpy.array
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
        """Fonction qui calcul les facteurs de weibull à partir des moments

        :param x: Coordonnée x.
        :type x: int
        :param y: Coordonnée y.
        :type y: int
        :return: Les facteurs de forme et d'échelle de Weibull.
        :rtype: list
        """

        raw_data = np.array([k for k in range(len(self.wind_histogram[x, y])) for i in range(int(self.wind_histogram[x, y, k]))])

        bin_centers = np.arange(0.5, 40.5)
        frequencies = self.wind_histogram[x, y]

        n = np.sum(frequencies)
        # Calcul du moment d'ordre 1 (moyenne)
        mean = np.sum(bin_centers * frequencies) / n
        # Calcul du moment d'ordre 2 (variance)
        var = np.sum(((bin_centers - mean) ** 2) * frequencies) / n
        # Calcul du moment d'ordre 3 (asymétrie)
        skewness = (np.sum(((bin_centers - mean) ** 3) * frequencies) / n) / (var ** (3/2))
        # Calcul du moment d'ordre 4 (kurtosis ?)
        kurtosis = ((np.sum(((bin_centers - mean) ** 4) * frequencies) / n) / (var ** 2)) - 3

        # Calculer estimation du facteur de forme
        shape = (kurtosis+3) / (skewness**2)
        # Calculer estimation du facteur d'échelle
        scale = mean / (sp.special.gamma(1 + 1/shape)**(1/shape))

        return [shape, scale]

    def get_moment_weibull_factors(self):
        """Fonction qui retourne les facteurs de Weibull à partir des moments pour chaque coordonnée.

        :return: Une matrice 2D contenant les facteurs de forme et d'échelle.
        :rtype: numpy.array
        """

        size_x, size_y = self.wind_mean.shape

        weibull = np.zeros((size_x, size_y, 2))

        for x in range(size_x):
            for y in range(size_y):
                weibull[x, y] = self.calculate_weibull_factors_with_moments(x, y)

        return weibull
