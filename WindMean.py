import numpy as np
import scipy as sp
import pandas as pd
import matplotlib.pyplot as plt
import warnings


class WindMean:

    def __init__(self, long_array, lat_array):
        self.grid = np.meshgrid(long_array, lat_array)
        size = np.shape(self.grid)[1:]
        self.wind_matrix = np.zeros((size[0], size[1]))
        self.stations_coordinates = np.array([]).reshape((0, 2))
        self.stations_values = np.array([])
        self.interp = None

    def add_station_data(self, file):
        """Ajouter les données d'un fichier

        :param file:
        :type file:
        :return:
        :rtype:
        """
        xx, yy = self.grid
        #print(xx, yy)
        df = pd.read_csv(file, index_col=0)
        extract_df = df[["longitude", "latitude", "wind_speed"]].sort_values(by=["longitude", "latitude"])
        coords = []
        values = []
        for (longitude, latitude, wind_speed) in np.array(extract_df):
            round_lon = round(longitude, ndigits=2)
            round_lat = round(latitude, ndigits=2)
            x, y = np.where(np.isclose(xx, round_lon, atol=1e-3) &
                            np.isclose(yy, round_lat, atol=1e-3))
            if np.any(x) and np.any(y):
                #print(round_lon, round_lat)
                coords.append([round_lon, round_lat])
                values.append(wind_speed)
        coords = np.array(coords)
        values = np.array(values)

        self.stations_coordinates = np.concatenate((self.stations_coordinates, coords))
        self.stations_coordinates = np.sort(self.stations_coordinates, axis=0)
        self.stations_values = np.concatenate((self.stations_values, values))
        self.stations_values = np.sort(self.stations_values)

    def interpolation_2D(self):
        xx, yy = self.grid
        x = self.stations_coordinates[:, 0]
        y = self.stations_coordinates[:, 1]
        data = self.stations_values
        print(data)
        self.wind_matrix = sp.interpolate.griddata((x, y), data, (xx, yy), method="nearest")
        plt.subplot(221)
        plt.imshow(self.wind_matrix)
        self.wind_matrix = sp.interpolate.griddata((x, y), data, (xx, yy), method="linear")
        plt.subplot(222)
        plt.imshow(self.wind_matrix)
        self.wind_matrix = sp.interpolate.griddata((x, y), data, (xx, yy), method="cubic")
        plt.subplot(223)
        plt.imshow(self.wind_matrix)
        plt.show()

    def weigth(self, point_coords, station_coords, ):
        x_ij, y_ij = point_coords[0], point_coords[1]
        x_k, y_k = station_coords[:, 0], station_coords[:, 1]

        sq_r = (x_ij - x_k)**2 + (y_ij - y_k)**2  # r²

        warnings.filterwarnings('error')  # https://stackoverflow.com/questions/15933741/how-do-i-catch-a-numpy-warning-like-its-an-exception-not-just-for-testing
        try:
            W_k = 1/sq_r
        except Warning:
            W_k = np.where(sq_r == 0, 1, 0)
        return W_k

    def interp_point(self, x_ij, y_ij):
        # Interpolation avec des poids. La c'est l'interpolation que pour 1 point

        # Source méthode bis plus complexe
        # https://www.researchgate.net/publication/234295032_A_Simple_Method_for_Spatial_Interpolation_of_the_Wind_in_Complex_Terrain

        nb_stations = len(self.stations_values)
        Wk = self.weigth([x_ij, y_ij], self.stations_coordinates)
        U_ij = np.sum(Wk*self.stations_values)/np.sum(Wk)
        return U_ij

    def interp_grid(self):
        xx, yy = self.grid
        vfunc = np.vectorize(self.interp_point)
        self.wind_matrix = vfunc(xx, yy)
