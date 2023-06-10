import numpy as np
import matplotlib.pyplot as plt


class WindField:

    def __init__(self, size):
        self.wind_matrix = np.zeros((size[0], size[1]))

    # Overload operator and classic functions : https://realpython.com/operator-function-overloading/
    def __add__(self, other):
        new_windfield = WindField(np.shape(self.wind_matrix))
        new_windfield.wind_matrix = self.wind_matrix + other.wind_matrix
        return new_windfield

    def __truediv__(self, other):
        new_windfield = WindField(np.shape(self.wind_matrix))
        if type(other) in (int, float):
            new_windfield.wind_matrix = self.wind_matrix/other
        return new_windfield

    def add_station_data(self, x, y, wind_speed):
        self.wind_matrix[x][y] = wind_speed

    def interpolation_2D(self):
        # A compléter
        return

    def interpolation_3D(self):
        # A compléter
        return

    @staticmethod
    def plot_windfield():
        ax = plt.figure().add_subplot(projection='3d')
        # Source de base : https://stackoverflow.com/questions/7130474/how-to-plot-a-3d-vector-field
