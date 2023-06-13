import numpy as np
import os
import pandas as pd


class Station:

    def __init__(self, station_id, longitude, latitude, elevation):
        self.id = station_id
        self.long = longitude
        self.lat = latitude
        self.elev = elevation

    def contains_wind_hourly(self, year):
        check_hourly_wind = False
        for root, dirpath, filenames in os.walk(f"./data/{self.id}/{year}"):
            if "Hourly" in root:
                for filename in filenames:
                    if "_W" in filename:
                        check_hourly_wind = True
        return check_hourly_wind

    def contains_wind_measurements_year(self, year):
        check_wind = False
        for root, dirpath, filenames in os.walk(f"./data/{self.id}/{year}"):
            for filename in filenames:
                if "_W" in filename:
                    check_wind = True
        return check_wind

    def contains_wind_measurements_period(self, period):
        check_period = []
        for year in period:
            check_period.append(self.contains_wind_measurements_year(year))
        return True in check_period

    def contains_temperature_measurements_year(self, year):
        check_temperature = False
        for root, dirpath, filenames in os.walk(f"./data/{self.id}/{year}"):
            for filename in filenames:
                if "_T" in filename:
                    check_temperature = True
        return check_temperature

    def contains_temperature_measurements_period(self, period):
        check_period = []
        for year in period:
            check_period.append(self.contains_temperature_measurements_year(year))
        return True in check_period
