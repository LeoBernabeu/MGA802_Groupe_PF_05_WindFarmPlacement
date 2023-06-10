import numpy as np
import requests


class Topography:
    # Trop lent. Regarder https://github.com/Jorl17/open-elevation/blob/master/docs/host-your-own.md ou Geopy

    def __init__(self, long_array, lat_array):
        len_x, len_y = len(long_array), len(lat_array)
        self.elev_matrix = np.zeros((len_x, len_y))
        for x in range(len_x):
            for y in range(len_y):
                elev = requests.get(f"http://geogratis.gc.ca/services/elevation/cdem/"
                                    f"altitude?lat={lat_array[y]}&lon={long_array[y]}").json()['altitude']
                print(long_array[x], lat_array[y], elev)
                self.elev_matrix[x, y] = elev
