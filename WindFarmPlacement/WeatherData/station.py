import glob
import os
import pandas as pd
import re


class Station:
    """Objet représentant une station météorologique.

    :param station_id: L'identifiant de la station météorologique.
    :type station_id: str
    :param latitude: La latitude de la station météorologique.
    :type latitude: float
    :param longitude: La longitude de la station météorologique.
    :type longitude: float
    """

    def __init__(self, station_id, latitude, longitude):
        self.id = station_id
        self.lat = latitude
        self.long = longitude
        self.df_wind_data = {}  # Un dico, on associe à la df

    def contains_wind_measurements_month(self, year, month):
        """Fonction qui vérifie si la station dispose de mesure sur le vent pour un mois précis d'une année donnée.

        :param year: L'année pour laquelle on veut vérifier la présence de données liées au vent.
        :type year: int
        :param month: Le mois de l'année sur lequel effectué la recherche.
        :type month: int
        :return: Retourne un booléen qui indique si la station dispose de données liées au vent.
        :rtype: bool
        """

        check_wind = False
        # On parcourt l'ensemble des fichiers présent dans le dossier au chemin indiqué dans le dossier 'data'
        for root, dirpath, filenames in os.walk(f"./data/{self.id}/{year}"):
            for filename in filenames:
                # On vérifie que le nom du fichier pour le mois 'month' contient l'indicatif _W
                if re.search(f"\\b{month}", filename) and "_W" in filename:
                    check_wind = True
        return check_wind

    def contains_wind_measurements_year(self, year):
        """Fonction qui vérifie si la station dispose de mesure sur le vent pour une année donnée.

        :param year: L'année pour laquelle on veut vérifier la présence de données liées au vent.
        :type year: int
        :return: Retourne un booléen qui indique si la station dispose de données liées au vent.
        :rtype: bool
        """

        check_wind = False
        # On parcourt l'ensemble des fichiers présent dans le dossier au chemin indiqué dans le dossier 'data'
        for root, dirpath, filenames in os.walk(f"./data/{self.id}/{year}"):
            for filename in filenames:
                # On vérifie que le nom du fichier pour le mois 'month' contient l'indicatif _W
                if "_W" in filename:
                    check_wind = True
        return check_wind

    def contains_wind_measurements_period(self, period):
        """Fonction qui vérifie si la station possède des mesures de vent pour une période donnée (liste d'années).

        :param period: La période (liste d'années) pour laquelle on veut vérifier la présence de données sur la vent.
        :type period: list[int]
        :return: True si des données sur la température sont disponibles pour au moins une année de la période, False
        sinon.
        :rtype: bool
        """
        check_temperature = False
        for year in period:
            if self.contains_wind_measurements_year(year):
                check_temperature = True
        return check_temperature

    # La température n'a finalement pas été utilisé jusqu'à présent.
    def contains_temperature_measurements_month(self, year, month):
        """Fonction qui vérifie si la station dispose de mesure sur la température pour un mois précis d'une année
        donnée.

        :param year: L'année pour laquelle on veut vérifier la présence de données liées à la température.
        :type year: int
        :param month: Le mois de l'année sur lequel effectué la recherche.
        :type month: int
        :return: Retourne un booléen qui indique si la station dispose de données liées à la température.
        :rtype: bool
        """

        check_wind = False
        # On parcourt l'ensemble des fichiers présent dans le dossier au chemin indiqué dans le dossier 'data'
        for root, dirpath, filenames in os.walk(f"./data/{self.id}/{year}"):
            for filename in filenames:
                # On vérifie que le nom du fichier pour le mois 'month' contient l'indicatif _W
                if re.search(f"\\b{month}", filename) and "_W" in filename:
                    check_wind = True
        return check_wind

    def contains_temperature_measurements_year(self, year):
        """Fonction qui vérifie si la station dispose de mesure sur la température pour une année donnée.

        :param year: L'année pour laquelle on veut vérifier la présence de données liées à la température.
        :type year: int
        :return: Retourne un booléen qui indique si la station dispose de données liées à la température.
        :rtype: bool
        """

        check_temperature = False
        # On parcourt l'ensemble des fichiers présent dans le dossier au chemin indiqué dans le dossier 'data'
        for root, dirpath, filenames in os.walk(f"./data/{self.id}/{year}"):
            for filename in filenames:
                # On vérifie que le nom du fichier pour le mois 'month' contient l'indicatif _T
                if "_T" in filename:
                    check_temperature = True
        return check_temperature

    def contains_temperature_measurements_period(self, period):
        """Fonction qui vérifie si la station possède des mesures de température pour une période donnée (liste d'années).

        :param period: La période (liste d'années) pour laquelle on veut vérifier la présence de données sur la température.
        :type period: list[int]
        :return: True si des données sur la température sont disponibles pour au moins une année de la période, False sinon.
        :rtype: bool
        """
        check_temperature = False
        for year in period:
            if self.contains_temperature_measurements_year(year):
                check_temperature = True
        return check_temperature

    def load_data(self, year, month):
        """Fonction qui charge les données liées au vent pour un mois et une année précisés en paramètres.
        Les données sont accessibles via l'attribut wind_data de la station.

        :param year: L'année des données à charger
        :type year: int
        :param month: Le mois des données à charger
        :type month: int
        :return: None
        """

        path = f"data/{self.id}/{year}"

        # glob : Retourne la liste des fichiers dont le name respecte le schéma passé en paramètre
        filename = glob.glob(path + "/" + f"{month}*.csv")[0]
        try:
            df = pd.read_csv(filename, usecols=[19])
        except ValueError:
            # Pour permettre d'ouvrir des fichiers avec un format différent de ceux de weather canada
            df = pd.read_csv(filename)
        # Conversion en m/s des vitesses
        df["Wind Spd (m/s)"] = df["Wind Spd (km/h)"]*1000/3600

        # On conserve uniquement les valeurs en m/s qui sont présentes, i.e : on ne garde pas les lignes vides.
        df_null = df["Wind Spd (m/s)"].notnull()
        df_data = df["Wind Spd (m/s)"].loc[df_null]

        # Sauvegarde sous la forme d'un dictionnaire.
        self.df_wind_data[month] = df_data

    def reset_data(self, month):
        """Fonction qui réinitialise l'attribut wind_data de la station pour oublier les données chargées précédemment.

        :param month: Le mois pour lequel on veut réinitialiser les données.
        :type month: int
        :return: None
        """
        self.df_wind_data[month] = {}

    def get_wind_data_timestamp(self, month, time_index):
        """Fonction qui renvoie la valeur de vitesse du vent à un instant précis (Heure : Jour) indiqué par son indice.
        L'indice correspond à la ligne correspondante du fichier csv.

        :param month: Le mois pour lequel on veut récupérer les données.
        :type month: int
        :param time_index: L'indice de l'instant précis dans les données.
        :type time_index: int
        :return: Retourne la vitesse du vent mesurée par la station
        :rtype: float
        """

        try:
            wind_speed = self.df_wind_data[month].loc[time_index]
        except (AttributeError, KeyError):
            # AttributeError s'il n'y a pas de données sur le mois ; IndexError s'il n'y a pas de données à time_index
            wind_speed = None
        return wind_speed
