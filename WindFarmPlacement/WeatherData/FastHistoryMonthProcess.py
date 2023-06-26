import numpy as np
from WindFarmPlacement.utils import number_days_for_month, interpolation
import logging
import multiprocessing


class FastHistoryMonthProcess(multiprocessing.Process):
    """En vrai avec multiprocessing, utiliser correctement il y a un résultat intéressant.
    Pour du 20x20, on divise par un peu plus que 2 le temps d'exécution.
    Test sur 50x50 : Méthode classique -> 380-420 sec
    Multi-process -> ~150 sec
    Et enfin 100x100 -> 650 contre 1580
    Conclusion : Apparemment c'est ce qu'il nous faut
    Eventuellement combiner à du multi-process sur les années mais avec trop d'années ça va nécessiter beaucoup de
    ressources (genre 10 ans = 10+120 process) donc peut-être en option"""

    def __init__(self, grid, stations, year, month, altitude, queue):
        super(FastHistoryMonthProcess, self).__init__()
        self.grid = grid
        self.stations = stations
        self.year = year
        self.month = month
        self.altitude = altitude
        self.queue = queue
        logging.debug(f'FastHistoryMonth - Threaded class {month} created')

    def run(self) -> None:

        logging.debug(f'FastHistoryMonth - Threaded class {self.month} just started')

        counter_div = 0
        xx, yy = self.grid
        size_x, size_y = xx.shape
        wind_mean = np.zeros_like(xx)
        wind_histogram = np.zeros((size_x, size_y, 40))

        for time in range(24*number_days_for_month(self.month)):  # On multiplie par 24 pour les heures d'une journée
            # À chaque instant, on récupère toutes les données disponibles auprès des stations
            wind_values = np.array([[wind_value, station.long, station.lat] for station in self.stations
                                    if (wind_value := station.get_wind_data_timestamp(self.month, time))])

            # Si on dispose d'au moins 4 valeurs de vent on effectue l'interpolation du champ.
            # (Arbitraire et reste très faible)
            if len(wind_values) > 4:
                counter_div += 1

                # Interpolation
                wind_field = interpolation(xx, yy, wind_values)
                if self.altitude:
                    wind_field = self.estimate_wind_speed_for_altitude(wind_field)

                # Mise à jour des statistiques et de la moyenne
                for x in range(size_x):
                    wind_histogram[x, np.arange(size_y), wind_field.astype(int)[x, :]] += 1

                wind_mean += wind_field

        if counter_div != 0:
            # Calcul du champ de vent moyen
            wind_mean = wind_mean / counter_div

        self.queue.put([wind_mean, wind_histogram])

        logging.debug(f'FastInterpolation - Threaded class {self.month} just finished')

    def estimate_wind_speed_for_altitude(self, wind):
        """Fonction qui estime la vitesse du vent à une altitude donnée en utilisant le profil vertical de la vitesse
        du vent
        """

        altitude_measures = 10  # Les capteurs des stations sont à 10 m du sol
        z = 0.03  # Longueur de rugosité
        estimate_factor = np.log(self.altitude/z)/np.log(altitude_measures/z)

        return wind*estimate_factor
