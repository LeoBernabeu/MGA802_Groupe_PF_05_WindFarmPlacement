import numpy as np
import scipy as sp
import pandas as pd


class WindMean:

    def __init__(self, long_array, lat_array):
        self.grid = np.meshgrid(long_array, lat_array)
        size = np.shape(self.grid)[1:]
        self.wind_matrix = np.zeros((size[0], size[1]))

    def add_station_data(self, file):
        # On part du principe qu'une vérif antérieur a été faite sur est-ce qu'il y a des mesures du vent
        xx, yy = self.grid
        df = pd.read_csv(file, index_col=0)
        for latitude, longitude, wind_speed in df[["Lonitude", "Latitude", "wind_speed"]]:
            x, y = np.argwhere((xx == round(latitude, ndigits=4)) & (yy == round(latitude, ndigits=4)))[0]
            self.wind_matrix[x][y] = wind_speed

    def interpolation_2D(self):
        # A compléter
        sp.interpolate.intep
        return
