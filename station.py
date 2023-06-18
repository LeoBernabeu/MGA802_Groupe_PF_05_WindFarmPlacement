import glob
import numpy as np
import os
import pandas as pd
import re


class Station:

    def __init__(self, station_id, latitude, longitude, elevation):
        self.id = station_id
        self.lat = latitude
        self.long = longitude
        self.elev = elevation
        self.wind_data = None

    def contains_wind_measurements_year(self, year):
        check_wind = False
        for root, dirpath, filenames in os.walk(f"./data/{self.id}/{year}"):
            for filename in filenames:
                if "_W" in filename:
                    check_wind = True
        return check_wind

    def contains_wind_measurements_month(self, year, month):
        check_wind = False
        for root, dirpath, filenames in os.walk(f"./data/{self.id}/{year}"):
            for filename in filenames:
                if re.search(f"\\b{month}", filename) and "_W" in filename:
                    check_wind = True
        return check_wind

    def contains_temperature_measurements_year(self, year):
        check_temperature = False
        for root, dirpath, filenames in os.walk(f"./data/{self.id}/{year}"):
            for filename in filenames:
                if "_T" in filename:
                    check_temperature = True
        return check_temperature

    def load_data(self, year, month):
        path = f"data/{self.id}/{year}"
        filename = glob.glob(path + "/" + f"{month}*.csv")[0]
        df = pd.read_csv(filename)
        df_speed = df["Wind Spd (km/h)"]
        wind_speeds = np.array(df_speed.loc[df_speed.notnull()])
        wind_times = np.where(df_speed.notnull())[0]

        # Conversion en m/s
        wind_speeds = wind_speeds * 1000 / 3600

        # Sauvegarde
        self.wind_data = dict(zip(wind_times, wind_speeds))

    def reset_data(self):
        self.wind_data = None

    def get_data_timestamp(self, index):
        try:
            wind_speed = self.wind_data[index]
        except (KeyError, TypeError):
            wind_speed = None
        return wind_speed

    def get_coordinates(self):
        coordinates = (self.lat, self.long)
        return coordinates
