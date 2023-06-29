import logging
import multiprocessing
import numpy as np

from WindFarmPlacement.utils import number_days_for_month, interpolation


class FastHistoryMonthProcess(multiprocessing.Process):
    """Processus de calcul rapide de l'historique pour un mois spécifique.

    :param grid: La grille du parc éolien.
    :type grid: tuple[np.ndarray, np.ndarray]
    :param stations: La liste des stations météorologiques.
    :type stations: list[Station]
    :param year: L'année correspondante au mois à traiter.
    :type year: int
    :param month: Le mois à traiter.
    :type month: int
    :param altitude: L'altitude de référence pour l'interpolation des données.
    :type altitude: float
    :param queue: La file d'attente pour le résultat du processus.
    :type queue: multiprocessing.Queue
    """

    def __init__(self, grid, stations, year, month, altitude, queue):
        super().__init__()
        self.grid = grid
        self.stations = stations
        self.year = year
        self.month = month
        self.altitude = altitude
        self.queue = queue
        # logging.debug(f'FastHistoryMonth - Threaded class {month} created')

    def run(self) -> None:
        """Exécute le processus de calcul rapide de l'historique pour un mois spécifique.

        :return:
        :rtype:
        """

        # Activer le débogage
        # logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )
        logging.debug(f'FastHistoryMonth - Threaded class {self.month} just started')

        xx, yy = self.grid
        size_x, size_y = xx.shape
        wind_mean = np.zeros_like(xx)
        wind_histogram = np.zeros((size_x, size_y, 40))

        counter_divide = 0  # Compteur pour la division final du champ de vent moyen
        for time in range(24*number_days_for_month(self.month)):  # On multiplie par 24 pour les heures d'une journée

            # À chaque instant, on récupère toutes les données disponibles auprès des stations
            wind_values = np.array([[wind_value, station.long, station.lat] for station in self.stations
                                    if (wind_value := station.get_wind_data_timestamp(self.month, time))])

            # On interpolle si on dispose d'au moins 10 valeurs pour que ça soit trop imprécis (Abritraire mais faible)
            if len(wind_values) > 10:
                counter_divide += 1

                # Interpolation
                wind_field = interpolation(xx, yy, wind_values)

                # Profil vertical du vent
                wind_field = self.estimate_wind_speed_for_altitude(wind_field)

                # Mise à jour des statistiques et du champ de vent moyen
                for x in range(size_x):
                    wind_histogram[x, np.arange(size_y), wind_field.astype(int)[x, :]] += 1
                wind_mean += wind_field

        # Calcul final du champ de vent moyen
        if counter_divide != 0:
            wind_mean = wind_mean / counter_divide

        # Ajout des statistiques et du champ moyen à la Queue pour être ensuite récupéré dans le processus parent
        self.queue.put([wind_mean, wind_histogram])

        # logging.debug(f'FastInterpolation - Threaded class {self.month} just finished')

    def estimate_wind_speed_for_altitude(self, wind):
        """Fonction qui estime la vitesse du vent à une altitude donnée en utilisant le profil vertical de la vitesse
        du vent

        :param wind: Le champ de vent initial.
        :type wind: np.ndarray
        :return: Le champ de vent estimé à l'altitude spécifiée.
        :rtype: np.ndarray
        """

        altitude_measures = 10  # Les capteurs des stations sont à 10 m du sol
        z = 0.03  # Longueur de rugosité (Terrain plat et dégagé : herbe, quelques obstacles isolés)
        estimate_factor = np.log(self.altitude/z)/np.log(altitude_measures/z)

        return wind*estimate_factor
