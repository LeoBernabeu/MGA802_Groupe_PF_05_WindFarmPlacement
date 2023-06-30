import numpy as np
import pandas as pd
from math import ceil

from WindFarmPlacement.utils import gather, rectangle

from WindFarmPlacement.WeatherData import Station
from WindFarmPlacement.WeatherData import WindHistory


class WindFarmPlacement:
    """Objet conceptuel représentant un "gestionnaire" qui s'occupe de faire le lien entre le calcul des données du
    vent dans la zone étudiée et la puissance productible par des éoliennes dans cette zone, afin de trouver les
    meilleures parcelles où placer un champ d'éoliennes.

    :param long_min: La longitude minimale de la zone d'étude.
    :type long_min: float
    :param long_max: La longitude maximale de la zone d'étude.
    :type long_max: float
    :param lat_min: La latitude minimale de la zone d'étude.
    :type lat_min: float
    :param lat_max: La latitude maximale de la zone d'étude.
    :type lat_max: float
    :param nb_lat: Le nombre de points en latitude pour l'échantillonnage de la zone.
    :type nb_lat: int
    :param nb_long: Le nombre de points en longitude pour l'échantillonnage de la zone.
    :type nb_long: int
    """

    def __init__(self, long_min, long_max, lat_min, lat_max, nb_lat, nb_long):
        self.long_array = np.linspace(long_min, long_max, nb_long)
        self.lat_array = np.linspace(lat_min, lat_max, nb_lat)
        self.wind_history = WindHistory(self.long_array, self.lat_array)

    def find_near_stations(self, radius, required_stations=100):
        """Fonction qui recherche les stations les plus proches de la zone d'étude à partir des données contenues dans
        le fichier d'inventaire de https://climate.weather.gc.ca. Le rayon de recherche autour de la zone d'étude est
        incrémenté jusqu'à trouver un minimum de 100 stations par défaut.

        :param radius: Rayon de recherche des stations autour de la zone d'étude.
        :type radius: int
        :param required_stations: Nombre minimum de stations a récupéré.
        :type required_stations: int
        :return: Retourne une liste des stations trouvées dans le rayon de recherche.
        :rtype: list[Station]
        """

        # Calcul des bornes de recherche sur la latitude et la longitude.
        lat_min, lat_max = self.lat_array[0] - radius, self.lat_array[-1] + radius
        long_min, long_max = self.long_array[0] - radius, self.long_array[-1] + radius

        # Création de la DataFrame avec les colonnes qui nous intéressent.
        df = pd.read_csv("Station_Inventory_EN.csv", usecols=(3, 6, 7), skiprows=3)

        # Recherche des stations dont la latitude et la longitude sont comprises dans l'intervalle de recherche.
        lat_index = np.array(df.index[df["Latitude (Decimal Degrees)"].between(lat_min, lat_max)])
        long_index = np.array(df.index[df["Longitude (Decimal Degrees)"].between(long_min, long_max)])
        good_index = np.intersect1d(lat_index, long_index)

        # Si le nombre de stations trouvées est insuffisant, on relance la recherche en augmentant le rayon.
        if len(good_index) < required_stations:
            stations = self.find_near_stations(radius+1)
        # Sinon, on crée une liste d'objets stations avec les données utiles.
        else:
            stations = []
            for index in good_index:
                station_id, lat, long = df.iloc[index]
                stations.append(Station(int(station_id), lat, long))
        return stations

    def get_wind_history_data_full_threaded(self, period, altitude):
        """Fonction qui récupère les données historiques de la zone d'étude pour une liste d'années et une altitude.
        Cette fonction utilise le parallélisme des tâches, pour pouvoir effectuer le traitement des données de tous
        les mois de chaque année en même temps. Attention : Peut nécessiter beaucoup de mémoire.

        :param period: Liste d'années à utiliser pour calculer l'historique du vent.
        :type period: list
        :param altitude: L'altitude de la mesure pour l'interpolation des données.
        :type altitude: int
        :return: None
        """

        near_stations = self.find_near_stations(1)
        usefull_stations = []
        # On ajoute les stations proches de la zone d'étude qui possèdent des données sur cette année.
        for station in near_stations:
            if station.contains_temperature_measurements_period(period):
                usefull_stations.append(station)

        self.wind_history.stations = usefull_stations
        self.wind_history.altitude = altitude

        self.wind_history.compute_history(period)

    def get_wind_history_data(self, period, altitude):
        """Fonction qui récupère les données historiques de la zone d'étude pour une liste d'années et une altitude.
        Cette fonction utilise le parallélisme des tâches, pour pouvoir effectuer le traitement des données de tous
        les mois en même temps. Les années sont traitées une à une. Cette méthode est à utiliser si
        'get_wind_history_data_full_threaded' requiert trop de mémoire pour votre machine.

        :param period: Liste d'années à utiliser pour calculer l'historique du vent.
        :type period: list
        :param altitude: L'altitude de la mesure pour l'interpolation des données.
        :type altitude: int
        :return: None
        """

        near_stations = self.find_near_stations(1)

        for year in period:

            useful_stations = []
            for station in near_stations:
                if station.contains_wind_measurements_period(period):
                    useful_stations.append(station)
            # On crée un nouveau WindHistory pour l'année d'étude
            wind_history = WindHistory(self.long_array, self.lat_array, useful_stations, altitude)
            # On lance le calcul des données historiques.
            wind_history.compute_history_year(year)

            self.wind_history += wind_history

    def find_adapted_zone(self, windfarm, turbine_spacing, nb_area=5):
        """Fonction qui recherche les parcelles de la zone d'étude qui permettent d'atteindre l'objectif de puissance à
        produire.

        :param windfarm: Un champ d'éolienne avec une puissance visée et ses éoliennes.
        :type windfarm: WindFarm
        :param turbine_spacing: Facteur d'espacement entre les éoliennes
        :type turbine_spacing: int
        :param nb_area: Nombre de zones maximum à renvoyer.
        :type nb_area: int
        :return: Les coordonnées des zones intéressantes et la puissance totale produite.
        :rtype: tuple[np.ndarray, np.ndarray]
        """

        # On commence par calculer les facteurs de la distribution de Weibull
        self.wind_history.get_fit_weibull_factors()
        weibull_factors = self.wind_history.weibull_factors

        # On calcule la largeur/longitude en longitude et latitude d'une cellule de notre grille.
        # (Remarque : On ne tient pas compte que la distance entre 2 degrès de longitude dépend de la latitude)
        width_lat_grid = (self.lat_array[1] - self.lat_array[0])
        width_long_grid = (self.long_array[1] - self.long_array[0])

        # On calcule les latitudes medianes de chaque cellule
        medians = (self.lat_array[:-1:1]+self.lat_array[1::1])/2
        # On calcule le nombre d'éoliennes maximum dans chaque cellule si on les dispose en rectangle
        maximum_windmills_in_cells = windfarm.maximum_windmills_in_rectangle_surface(turbine_spacing, medians,
                                                                                     width_long_grid)

        # On calcule ensuite la puissance maximum théorique pouvant être produite pour chaque cellule
        total_power = windfarm.total_theoretical_produced_power(weibull_factors, maximum_windmills_in_cells)

        # On filtre pour garder les coordonnées des puissances qui atteignent l'objectif et on regarde celles contiguës
        clusters = gather(total_power > windfarm.target_power)

        area_of_interest_coordinates = None
        # S'il y a des ensembles de cellules qui respectent l'objectif de puissance
        if clusters:
            # On calcule l'espacement théorique nécessaire entre les éoliennes
            lat_spacing, long_spacing = windfarm.calculate_theorical_spacing(turbine_spacing,
                                                                             np.median(self.lat_array))

            # On calcule la largeur/longueur en longitude et latitude nécessaire pour aligner toutes les éoliennes
            width_lat, width_long = len(windfarm.windmills)*lat_spacing, len(windfarm.windmills)*long_spacing

            # On calcule la taille de nombre des cellules des clusters pour pouvoir disposer les éoliennes en ligne
            # quelle que soit la direction.
            width_x, width_y = ceil(width_long / width_long_grid), ceil(width_lat / width_lat_grid)

            # On cherche toutes les zones rectangulaires
            rectangular_areas = []
            for i in range(len(clusters)):
                rectangular_areas.extend(rectangle(clusters[i], width_x, width_y))

            if len(rectangular_areas) > nb_area:
                # On trie les rectangles selon la puissance théorique max et on ne garde que les 'nb_area' meilleures.
                arg_sort = np.zeros(len(rectangular_areas))
                for i in range(len(rectangular_areas)):
                    column_start, column_end = rectangular_areas[i][0], rectangular_areas[i][1]
                    rows = rectangular_areas[i][2]
                    # On extrait la sous_matrice qui correspond à la zone d'intérêt
                    sub_power_matrix = total_power[rows, column_start:column_end]
                    # On trie les zones d'intérêts selon la puissance maximum quels permettent de produire
                    arg_sort[i] = np.mean(sub_power_matrix)
                # On trie les indices selon l'ordre décroissant des puissances
                sort_index = np.argsort(-arg_sort)
                rectangular_areas = [rectangular_areas[sort_index[k]] for k in range(nb_area)]

            # Les rectangles sont sélectionnés, on va renvoyer à la place des couples de longitudes et de latitudes
            area_of_interest_coordinates = np.zeros((len(rectangular_areas), 2, 2))

            # On récupère la liste des indices colonnes du rectange (i.e : latitudes)
            rows = np.array([rectangular_areas[k][2] for k in range(len(rectangular_areas))])
            # On récupère les indices des premières et dernières lignes du rectangle sur la latitude (i.e : longitudes)
            limits = np.array([np.arange(rectangular_areas[k][0], rectangular_areas[k][1])
                               for k in range(len(rectangular_areas))])

            # On récupère les longitudes correspondantes
            longitudes = np.array(self.long_array[limits])
            # Une cellule ne correspond qu'à une coordonnée de longitude, cependant elle s'étend jusqu'à la longitude
            # suivante
            lon_limits = [np.min(longitudes, axis=1)-width_lat_grid/2, np.max(longitudes, axis=1)+width_lat_grid/2]
            area_of_interest_coordinates[:, 1, 0] = lon_limits[0]
            area_of_interest_coordinates[:, 1, 1] = lon_limits[1]

            # On récupère les longitudes correspondantes. (Contre intuitive, les indices partent du haut de la matrice,
            # i.e de la fin des array
            latitudes = np.array(self.lat_array[-(rows+1)])
            lat_limits = [np.min(latitudes, axis=1)-width_long_grid/2, np.max(latitudes, axis=1)+width_long_grid/2]
            area_of_interest_coordinates[:, 0, 0] = lat_limits[0]
            area_of_interest_coordinates[:, 0, 1] = lat_limits[1]

        return area_of_interest_coordinates, total_power
