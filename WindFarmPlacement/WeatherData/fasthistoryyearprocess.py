import logging
import multiprocessing
import numpy as np

from .fasthistorymonthprocess import FastHistoryMonthProcess


class FastHistoryYearProcess(multiprocessing.Process):
    """Processus de calcul rapide de l'historique sur une année spécifique.

    :param grid: La grille du parc éolien.
    :type grid: tuple[np.ndarray, np.ndarray]
    :param stations: La liste des stations météorologiques.
    :type stations: list[Station]
    :param year: L'année à traiter.
    :type year: int
    :param altitude: L'altitude de référence pour l'interpolation des données.
    :type altitude: float
    :param queue: La file d'attente pour le résultat du processus.
    :type queue: multiprocessing.Queue
    """

    def __init__(self, grid, stations, year, altitude, queue):
        super().__init__()
        self.grid = grid
        self.stations = stations
        self.year = year
        self.altitude = altitude
        self.queue = queue
        logging.debug(f'FastYear - Threaded class {year} created')

    def run(self) -> None:
        """Exécute le processus de calcul rapide de l'historique sur une année spécifique.

        :return:
        :rtype:
        """

        # Activer le débogage
        # logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )
        logging.debug(f"FastYear - Threaded class {self.year} started")

        follow_threads = []
        for month in range(1, 13):

            # Chargement des données par les stations pour le mois étudié
            for station in self.stations:
                # Si la station a des données sur ce mois elle les charge
                if station.contains_wind_measurements_month(self.year, month):
                    station.load_data(self.year, month)
                # Dans le cas contraire, on s'assure de ne pas garder d'anciennes données qui ne concernent pas ce mois
                else:
                    station.reset_data(month)

            threaded_q = multiprocessing.Queue()
            # Création des processus pour les calculs sur chaque mois
            threaded_interpolation = FastHistoryMonthProcess(self.grid, self.stations, self.year, month, self.altitude,
                                                             threaded_q)
            follow_threads.append((threaded_interpolation, threaded_q))

        xx, yy = self.grid
        size_x, size_y = xx.shape
        wind_year_mean = np.zeros_like(xx)
        wind_year_histogram = np.zeros((size_x, size_y, 40))

        # Lancement de l'exécution des processus
        for thread in follow_threads:
            thread[0].start()

        counter_divide = 0  # Compteur pour la division final du champ de vent moyen
        # Terminaison des processus
        for thread_and_queue in follow_threads:
            # On récupère le contenu des Queues
            wind_mean, wind_histogram = thread_and_queue[1].get()
            thread_and_queue[0].join()
            # Mise à jour de la moyenne et des statistiques
            wind_year_mean += wind_mean
            wind_year_histogram += wind_histogram
            counter_divide += 1

        # Calcul final du champ de vent moyen
        if counter_divide != 0:
            wind_year_mean = wind_year_mean/counter_divide

        # Ajout des statistiques et du champ moyen à la Queue pour être ensuite récupéré dans le processus parent
        self.queue.put([wind_year_mean, wind_year_histogram])
