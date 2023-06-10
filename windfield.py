import numpy as np


class WindField:

    def __init__(self, long_array, lat_array):
        self.wind_matrix = np.zeros((len(long_array), len(lat_array)))

    def add_station_data(self, x, y, wind_speed):
        self.wind_matrix[x][y] = wind_speed

    def interpolation_2D(self):
        # A compléter
        return
