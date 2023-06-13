import numpy as np
import pandas as pd
from archive.station import Station
from archive.windhistory import WindHistory


class StudyArea:

    stations = []
    windmills = []
    history = None

    def __init__(self, longitude_min, longitude_max, latitude_min, latitude_max):
        self.long_min, self.long_max = longitude_min, longitude_max
        self.lat_min, self.lat_max = latitude_min, latitude_max
        self.find_stations()

    def find_stations(self):
        df = pd.read_csv("../Station_Inventory_EN.csv", skiprows=3)
        long_index = np.array(df.index[df["Longitude (Decimal Degrees)"].between(self.long_min, self.long_max)])
        lat_index = np.array(df.index[df["Latitude (Decimal Degrees)"].between(self.lat_min, self.lat_max)])
        good_index = np.intersect1d(long_index, lat_index)
        for index in good_index:
            station_id, long, lat, elev = df.iloc[index][["Station ID", "Longitude (Decimal Degrees)",
                                                          "Latitude (Decimal Degrees)", "Elevation (m)"]]
            self.stations.append(Station(station_id, long, lat, elev))

    def init_wind_history(self, period):
        long_array = np.arange(self.long_min, self.long_max)
        lat_array = np.arange(self.lat_min, self.lat_max)
        self.history = WindHistory(long_array, lat_array, period)
        for station in self.stations:
            self.history.add_station_data(station)

    def add_windmill(self, windmill):
        self.windmills.append(windmill)