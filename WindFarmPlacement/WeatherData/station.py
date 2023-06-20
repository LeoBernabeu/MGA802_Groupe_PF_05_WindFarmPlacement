import glob
import os
import pandas as pd
import re


class Station:

    def __init__(self, station_id, latitude, longitude, elevation):
        self.id = station_id
        self.lat = latitude
        self.long = longitude
        self.elev = elevation
        self.df_wind_data = None

    def contains_wind_measurements_year(self, year):
        """Fonction qui vérifie si la station dispose de mesure sur le vent pour une année donnée.

        :param year : L'année pour laquelle on veut vérifier la présence de données liées au vent.
        :type year : int
        :return: Retourne un booléen qui indique si la station dispose de données liées au vent.
        :rtype : bool
        """

        check_wind = False
        for root, dirpath, filenames in os.walk(f"./data/{self.id}/{year}"):
            for filename in filenames:
                if "_W" in filename:
                    check_wind = True
        return check_wind

    def contains_wind_measurements_month(self, year, month):
        """Fonction qui vérifie si la station dispose de mesure sur le vent pour un mois précis d'une année donnée.

        :param year : L'année pour laquelle on veut vérifier la présence de données liées au vent.
        :type year : int
        :param month : Le mois de l'année sur lequel effectué la recherche.
        :type month : int
        :return: Retourne un booléen qui indique si la station dispose de données liées au vent.
        :rtype : bool
        """

        check_wind = False
        for root, dirpath, filenames in os.walk(f"./data/{self.id}/{year}"):
            for filename in filenames:
                if re.search(f"\\b{month}", filename) and "_W" in filename:
                    check_wind = True
        return check_wind

    def contains_temperature_measurements_year(self, year):
        """Fonction qui vérifie si la station dispose de mesure sur la température pour une année donnée.

        :param year : L'année pour laquelle on veut vérifier la présence de données liées à la température.
        :type year : int
        :return: Retourne un booléen qui indique si la station dispose de données liées à la température.
        :rtype : bool
        """

        check_temperature = False
        for root, dirpath, filenames in os.walk(f"./data/{self.id}/{year}"):
            for filename in filenames:
                if "_T" in filename:
                    check_temperature = True
        return check_temperature

    def load_data(self, year, month):
        """Fonction qui charge les données liées au vent pour un mois et une année précisés en paramètres.
        Les données sont accessibles via l'attribut wind_data de la station.

        :param year : L'année des données à charger
        :type year : int
        :param month : Le mois des données à charger
        :type month : int
        :return:
        :rtype :
        """

        path = f"heavy_data/{self.id}/{year}"

        # glob : Retourne la liste des fichiers dont le name respecte le schéma passé en paramètre
        filename = glob.glob(path + "/" + f"{month}*.csv")[0]
        df = pd.read_csv(filename, usecols=[19])
        # Conversion en m/s des vitesses
        df["Wind Spd (m/s)"] = df["Wind Spd (km/h)"]*1000/3600

        # On conserve uniquement les valeurs en m/s qui sont présentes, i.e : on ne garde pas les lignes vides.
        df_null = df["Wind Spd (m/s)"].notnull()
        df_data = df["Wind Spd (m/s)"].loc[df_null]

        # Sauvegarde sous la forme d'un dictionnaire.
        self.df_wind_data = df_data

    def reset_data(self):
        """Fonction qui réinitialise l'attribut wind_data de la station pour oublier les données chargées précédemment.

        :return:
        :rtype :
        """
        self.df_wind_data = None

    def get_wind_data_timestamp(self, time_index):
        """Fonction qui renvoie la valeur de vitesse du vent à un instant précis (Heure : Jour) indiqué par son indice.
        L'indice correspond à la ligne correspondante du fichier csv. Lorsque pl

        :param time_index :
        :type time_index : int
        :return: Retourne la vitesse du vent mesurée par la station
        :rtype : float
        """

        try:
            wind_speed = self.df_wind_data.iloc[time_index]
        except (AttributeError, IndexError):
            # AttributeError s'il n'y a pas de données sur le mois ; IndexError s'il n'y a pas de données à time_index
            wind_speed = None
        return wind_speed
