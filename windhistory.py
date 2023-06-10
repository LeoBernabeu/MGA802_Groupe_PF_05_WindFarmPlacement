import glob
import numpy as np
import pandas as pd
from windfield import WindField


class WindHistory:

    def __init__(self, long_array, lat_array, period):
        # period : réfléchir au format, pour l'instant liste des années
        nb = len(period)*365  # On prend que le Daily pour l'instant, on verra plus tard
        self.period = period
        self.grid = np.meshgrid(long_array, lat_array)
        size = np.shape(self.grid)[1:]
        self.windfields = np.array([WindField(size) for k in range(nb)])

    def add_station_data(self, station):
        # On part du principe qu'une vérif antérieur a été faite sur est-ce qu'il y a des mesures du vent
        xx, yy = self.grid
        x, y = np.argwhere((xx == station.long) & (yy == station.lat))[0]

        i = 0
        for year in self.period:
            path = f"data/{station.id}/{year}"
            filename = glob.glob(path + "Daily*.csv")
            df = pd.read_csv(filename)
            for wind_speed in np.array(df["Spd of Max Gust (km/h)"]):
                self.windfields[i].add_station_data(x, y, wind_speed)
                i += 1

    def wind_mean(self):
        # En vrai je ne sais pas si on garde en partie l'efficacité de numpy
        return np.mean(self.windfields)

    def find_area_of_interest(self):
        # A compléter
        return
