import threading
import logging
import numpy as np

from WindFarmPlacement.utils import interpolation


class FastInterpolation(threading.Thread):
    """Premier essai : on créé un thread par interpolation.
    Conclusion : Trop de threads, le programme est fortement ralenti.
    Deuxième essai : on crée un thread par mois.
    Conclusion : Ralenti pour créer les threads vers la moitié.
    Correction deuxième essai : on ne lance qu'une fois qu'ils sont tous créés.
    Conclusion : C'est toujours plus lent, mais c'est bien meiux.
    Test correction premier essai : on fait la même chose pour le premier.
    Conclusion : Même conclusion.

    Donc je pense qu'il y a trop de création et terminaison de threads, ce qui fait perdre beaucoup de temps.
    Je vais ramener les threads au niveau d'un mois."""

    def __init__(self, grid, stations, time, args=()):
        # On exécute le constructeur de la classe Thread
        super().__init__()
        # Constructeur propre à notre class
        self.stations = stations
        self.time = time
        self.grid = grid
        # On définit la queue pour partager la matrice interpolée
        self.queue = args
        logging.debug(f'FastInterpolation - Threaded class {time} just started')

    def run(self):

        xx, yy = self.grid
        # On récupère toutes les données disponibles auprès des stations
        wind_values = np.array([[wind_value, station.long, station.lat] for station in self.stations
                               if (wind_value := station.get_wind_data_timestamp(self.time))])

        wind_values = interpolation(xx, yy, wind_values)
        self.queue.put(interpolation(xx, yy, wind_values))

        logging.debug(f'FastInterpolation - Threaded class {self.time} just finished')




