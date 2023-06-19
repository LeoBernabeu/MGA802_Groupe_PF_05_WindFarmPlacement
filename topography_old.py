import numpy as np
import requests


class Topography:
    # Trop lent. Regarder https://github.com/Jorl17/open-elevation/blob/master/docs/host-your-own.md ou Geopy

    def __init__(self, long_array, lat_array):
        len_x, len_y = len(long_array), len(lat_array)
        self.elev_matrix = np.zeros((len_x, len_y))
        for x in range(len_x):
            for y in range(len_y):
                elev = requests.get(f"https://epqs.nationalmap.gov/v1/json?x={lat_array[y]}&y={long_array[y]}"
                                    f"&units=Meters&wkid=4326&includeDate=False/").json()
                print(long_array[x], lat_array[y], elev)
                self.elev_matrix[x, y] = elev
