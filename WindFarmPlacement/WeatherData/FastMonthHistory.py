import threading
import numpy as np
from WindFarmPlacement.utils import number_days_for_month, interpolation
import logging
import multiprocessing


class FastMonthHistory(threading.Thread):
    """Troisième essai : On fait les 12 mois en parallèle.
    Problème : on ne peut pas charger les douze mois en même temps. (Si c'est bon, c'est réglé)
    Conclusion : Après test sur du 20x20, temps d'exécution très proche +4-5 secondes.
    Tester sur du 50x50 = Très léger gain de temps -11-12 secondes.
    Dernier test sur du 100x100 -> 1720 secondes (Presque 29 minutes) contre 1557 ?
    Pourquoi maintenant c'est plus long ... La je suis repassé à 1583 ce qui sensiblement identique."""

    def __init__(self, grid, stations, year, month, altitude, queue):
        super().__init__()
        self.grid = grid
        self.stations = stations
        self.year = year
        self.month = month
        self.altitude = altitude
        self.queue = queue
        logging.debug(f'FastHistoryMonth - Threaded class {month} created')

    def run(self):

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

        self.queue.put(wind_histogram)
        logging.debug(f'FastInterpolation - Threaded class {self.month} just finished')

    def estimate_wind_speed_for_altitude(self, wind):
        """Fonction qui estime la vitesse du vent à une altitude donnée en utilisant le profil vertical de la vitesse
        du vent
        """

        altitude_measures = 10  # Les capteurs des stations sont à 10 m du sol
        z = 0.03  # Longueur de rugosité
        estimate_factor = np.log(self.altitude/z)/np.log(altitude_measures/z)

        return wind*estimate_factor
