import numpy as np
import pandas as pd
from station import Station


class StudyArea:

    def __init__(self, longitude_min, longitude_max, latitude_min, latitude_max):
        self.long_min, self.long_max = longitude_min, longitude_max
        self.lat_min, self.lat_max = latitude_min, latitude_max
        self.stations = []
        self.find_stations()

    def find_stations(self):
        df = pd.read_csv("Station_Inventory_EN.csv", skiprows=3)
        long_index = np.array(df.index[df["Longitude (Decimal Degrees)"].between(self.long_min, self.long_max)])
        lat_index = np.array(df.index[df["Latitude (Decimal Degrees)"].between(self.lat_min, self.lat_max)])
        good_index = np.intersect1d(long_index, lat_index)
        for index in good_index:
            station_id, long, lat, elev = df.iloc[index][["Station ID", "Longitude (Decimal Degrees)",
                                                          "Latitude (Decimal Degrees)", "Elevation (m)"]]
            self.stations.append(Station(station_id, long, lat, elev))

