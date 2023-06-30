import matplotlib.pyplot as plt
import numpy as np
import os

from math import ceil


class WindFarm:
    """Objet représentant un parc éolien.

    :param target_power: Puissance cible du parc éolien.
    :type target_power: float
    :param windmills: Liste des éoliennes du parc éolien (facultatif).
    :type windmills: list, optional
    :param topography: Topographie de la zone d'implantation du parc éolien (facultatif).
    :type topography: np.ndarray, optional
    """

    def __init__(self, target_power, windmills=None, topography=None):
        self.target_power = target_power
        if windmills is None:
            # Apparemment Pycharm dit que c'est mieux d'écrire comme ça
            self.windmills = []
        self.topography = topography
        self.blade_length = {}

    def add_windmill(self, windmill):
        """Fonction qui ajoute une éolienne au parc éolien.

        :param windmill: Éolienne à ajouter.
        :type windmill: Windmill
        """

        self.windmills.append(windmill)
        try:
            self.blade_length[windmill.blade_length] += 1
        except KeyError:
            self.blade_length[windmill.blade_length] = 1

    def total_theoretical_produced_power(self, weibull_factors, maximum_windmills):
        """Fonction qui calcule la puissance théorique totale que le parc éolien pourrait produire en fonction des
        facteurs de Weibull.

        :param weibull_factors: Matrice des facteurs de forme et d'échelle de Weibul.
        :type weibull_factors: np.ndarray
        :param maximum_windmills: Matrice du nombre maximum d'éoliennes pouvant être présente pour chaque cellule
        :type maximum_windmills: np.ndarray
        :return: Puissance théorique totale pouvant être produite par le parc éolien.
        :rtype: float
        """

        asc_sorted_keys = np.sort(list(self.blade_length.keys()))
        sorted_keys = np.flip(asc_sorted_keys)

        total_theoric_power = np.zeros(weibull_factors.shape[:2])

        for key in sorted_keys:
            nb_eol = self.blade_length[key]
            i = 0
            while self.windmills[i].blade_length != key:
                i += 1
            maximum_windmills -= nb_eol
            mask = maximum_windmills < 0
            if ~mask.any():
                total_theoric_power = nb_eol*self.windmills[i].theoretical_power(weibull_factors)
            else:
                copy_maximum_windmills = np.copy(maximum_windmills)
                copy_maximum_windmills[~mask] = 0

                copy_weibull_factors = np.copy(weibull_factors)
                copy_weibull_factors[~mask] = [0, 0]

                total_theoric_power -= copy_maximum_windmills*self.windmills[i].theoretical_power(copy_weibull_factors)

                maximum_windmills[mask] = np.nan

            if ~mask.all():
                break

        return total_theoric_power

    def total_precise_theorical_produced_power(self, weibull_factors, grid):
        """Calcul la puissance en tenant compte des positions des éoliennes

        :param weibull_factors: Matrice des facteurs de forme et d'échelle de Weibul.
        :type weibull_factors: np.ndarray
        :param grid:
        :type grid:
        :return:
        :rtype:
        """

        xx, yy = grid

        theorical_power = 0
        for windmill in self.windmills:
            # Recherche des indices correspondant dans la grille
            index_i = np.abs(xx[0] - windmill.lon).argmin()
            index_j = np.abs(yy[:, 0] - windmill.lat).argmin()
            shape, scale = weibull_factors[index_i, index_j]
            theorical_power += windmill.theorical_power_tuple_weibull_factors(shape, scale)
        return theorical_power

    def largest_blade_in_windfarm(self):
        """Fonction qui retourne la plus grande longueur de pâle parmi les éoliennes du champ.

        :return:
        :rtype:
        """
        blade_lengths = np.array([windmill.blade_length for windmill in self.windmills])
        return np.max(blade_lengths)

    def calculate_theorical_spacing(self, turbine_spacing, median_latitude):
        """Fonctionne qui calcule l'espacement théorique entre les éoliennes en prenant pour référence
        l'éolienne la plus grande du champ.

        :param turbine_spacing: Facteur d'espacement entre les éoliennes
        :type turbine_spacing: int
        :param median_latitude: La médiane des coordonnées de latitude de la zone où sont présentes les éoliennes.
        :type median_latitude: float
        :return: Renvoie l'espacement théorique pour la latitude et la longitude en degrés.
        :rtype: float, float
        """
        rotor_diameter = self.largest_blade_in_windfarm()
        spacing = turbine_spacing * rotor_diameter
        # Conversion en latitude (~111000 mètres par degré)
        lat_spacing = spacing / 111000
        # Conversion en longitude (~111000 mètres par degré, ajusté par la latitude)
        long_spacing = spacing / (111000 * np.cos(np.radians(median_latitude)))
        return lat_spacing, long_spacing

    def maximum_windmills_in_rectangle_surface(self, turbine_spacing, median_latitude, width_long):
        """Fonction qui calcule le nombre maximum d'éoliennes pouvant être disposer en rectangle dans une parcelle de
        terrain, en prenant pour référence l'éolienne la plus grande du champ.

        :param turbine_spacing: Facteur d'espacement entre les éoliennes
        :type turbine_spacing: int
        :param median_latitude: La médiane des coordonnées de latitude de la zone où sont présentes les éoliennes.
        :type median_latitude: float
        :param width_long: La largeur en longitude de la zone
        :type width_long: float
        :return: Le nombre maximum d'éolienne
        :rtype: int
        """

        lat_spacing, long_spacing = self.calculate_theorical_spacing(turbine_spacing, median_latitude)
        nb_eol = ceil(len(self.windmills)**.5)
        # On est toujours limité par la longitude qui est plus étroite sauf à l'équateur
        max_lon = np.floor(width_long/(nb_eol*long_spacing))
        return max_lon**2

    def place_windmills(self, area_of_interest, turbine_spacing):
        """Fonction qui place les éoliennes dans la zone d'intérêt spécifiée et affiche leur localisation sur un
        graphique 2D.

        :param area_of_interest: Zone d'intérêt spécifiée sous la forme ((lat_min, lat_max), (lon_min, lon_max)).
        :type area_of_interest: tuple
        :param turbine_spacing: Facteur d'espacement entre les éoliennes
        :type turbine_spacing: int
        :return: Coordonnées des éoliennes du parc éolien.
        :rtype: np.ndarray
        """

        # print(area_of_interest)
        num_windmills = len(self.windmills)

        lat_min, lat_max = area_of_interest[0]
        lon_min, lon_max = area_of_interest[1]

        # Calcul du centre de la petite section
        lat_center = (lat_min + lat_max) / 2
        lon_center = (lon_min + lon_max) / 2

        latitudes, longitudes = [], []
        latitudes.append(lat_center)
        longitudes.append(lon_center)

        # Espacement des éoliennes autour de l'éolienne centrale sous forme de quadrillage
        row_spacing, col_spacing = self.calculate_theorical_spacing(turbine_spacing, lat_center)

        # Initialisation variable pour déplacement en spirale
        row, col = 0, 0
        dep_row, dep_col = 1, 0
        step, count = 1, 0
        
        i = 0
        while i < num_windmills:
            print(row, col, dep_row, dep_col, count, step)

            new_latitude = lat_center + row*row_spacing
            new_longitude = lon_center + col*col_spacing
            self.windmills[i].set_coordinates(new_latitude, new_longitude)
            latitudes.append(new_latitude)
            longitudes.append(new_longitude)

            i += 1
            count += 1

            # Déplacement en spiral
            row += dep_row
            col += dep_col
            
            # Vérifier si on a atteint le nombre de pas requis dans la direction courante
            if count == step:
                # Changer de direction
                dep_row, dep_col = -dep_col, dep_row
                count = 0

            # Augmenter le nombre de pas à effectuer dans la nouvelle direction
            if 0 <= col == step or 0 > col == -(step-1):
                step += 1

        windmill_coordinates = np.vstack((latitudes, longitudes)).T

        # Create a figure
        fig, ax = plt.subplots()

        # Display windmill locations on a 2D plot
        ax.scatter(windmill_coordinates[:, 1], windmill_coordinates[:, 0], color='red', marker='x', label="windmill")

        ax.axis('auto')

        # Formater les étiquettes des axes en notation décimale
        ax.xaxis.set_major_formatter('{x:.3f}')
        ax.yaxis.set_major_formatter('{x:.3f}')

        # Set labels
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

        # Set title
        ax.set_title('Location of wind turbines in the farm')

        # Save the figure to the "figures" sub-folder
        current_directory = os.path.dirname(os.path.abspath(__file__))
        current_directory = current_directory.replace("\\WindFarmPlacement\\WindFarm", "")
        file_name = "Wind_turbines_locations.png"
        figure_path = os.path.join(current_directory, "figures", file_name)
        plt.savefig(figure_path)

        plt.show()

        return windmill_coordinates
