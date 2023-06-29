import numpy as np
import logging
import multiprocessing

from WindFarmPlacement.WeatherData.fasthistorymonthprocess import FastHistoryMonthProcess


class FastHistoryYearProcess(multiprocessing.Process):

    def __init__(self, grid, stations, year, altitude, queue):
        super().__init__()
        self.grid = grid
        self.stations = stations
        self.year = year
        self.altitude = altitude
        self.queue = queue
        # logging.debug(f'FastYear - Threaded class {year} created')

    def run(self) -> None:
        # logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )

        # logging.debug(f"FastYear - Threaded class {self.year} started")
        follow_threads = []
        for month in range(1, 13):
            # Chargement des données du mois étudié chez les stations
            for station in self.stations:
                # Si la station à des données sur ce mois elle les charge
                if station.contains_wind_measurements_month(self.year, month):
                    station.load_data(self.year, month)
                # Dans le cas contraire, on s'assure de ne pas garder d'anciennes données qui ne concernent pas ce mois.
                else:
                    station.reset_data(month)

            # logging.debug(f'Data loaded')

            threaded_q = multiprocessing.Queue()
            threaded_interpolation = FastHistoryMonthProcess(self.grid, self.stations, self.year, month, self.altitude,
                                                             threaded_q)
            follow_threads.append((threaded_interpolation, threaded_q))

        xx, yy = self.grid
        size_x, size_y = xx.shape
        wind_year_mean = np.zeros_like(xx)
        wind_year_histogram = np.zeros((size_x, size_y, 40))

        for thread in follow_threads:
            thread[0].start()

        count_div = 0
        for thread_and_queue in follow_threads:
            wind_mean, wind_histogram = thread_and_queue[1].get()
            thread_and_queue[0].join()
            wind_year_mean += wind_mean
            wind_year_histogram += wind_histogram
            count_div += 1

        wind_year_mean = wind_year_mean/count_div
        self.queue.put([wind_year_mean, wind_year_histogram])
