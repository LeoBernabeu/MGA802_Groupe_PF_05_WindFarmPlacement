import matplotlib.pyplot as plt
import numpy as np
import os


class WindFarm:

    def __init__(self, target_power, windmills=None, topography=None):
        self.target_power = target_power
        if windmills is None:
            # Apparemment Pycharm dit que c'est mieux d'écrire comme ça
            self.windmills = []
        self.topography = topography

    def add_windmill(self, windmill):
        self.windmills.append(windmill)

    def set_topography(self, topography):
        self.topography = topography

    def total_produced_power(self, wind_field):
        total_power = 0
        for windmill in self.windmills:
            total_power += windmill.produced_power(wind_field[windmill.lat, windmill.lon])
        return total_power

    def total_theoretical_produced_power(self, weibull_factors):
        total_theoric_power = 0
        for windmill in self.windmills:
            total_theoric_power += windmill.theoretical_power(weibull_factors)
        return total_theoric_power

    def place_windmills(self, area_of_interest,turbine_spacing):

        windmill = self.windmills[0]
        rotor_diameter = windmill.blade_length  # Espacement de 5 fois le diamètre (à définir par l'utilisateur)
        distance = turbine_spacing * rotor_diameter

        # print(area_of_interest)
        num_windmills = len(self.windmills)

        lat_min, lat_max = area_of_interest[0]
        lon_min, lon_max = area_of_interest[1]

        # Calculer le pas en latitude et en longitude pour les sections
        lat_step = (lat_max - lat_min) / num_windmills
        lon_step = (lon_max - lon_min) / num_windmills

        latitudes, longitudes = [], []

        # Calcul du centre de la petite section
        lat_center = (lat_min + lat_max) / 2
        lon_center = (lon_min + lon_max) / 2

        windmill.set_coordinates(lat_center, lon_center)

        latitudes.append(lat_center)
        longitudes.append(lon_center)

        windmill.set_coordinates(lat_min + lat_step, lon_min + lon_step)

        # Calculer le nombre de lignes et de colonnes pour le quadrillage
        num_rows = int(np.sqrt(num_windmills))
        num_cols = num_windmills // num_rows

        # Espacement des éoliennes autour de l'éolienne centrale sous forme de quadrillage
        row_spacing = distance / 111000  # Conversion en latitude (~111000 mètres par degré)
        col_spacing = distance / (111000 * np.cos(np.radians(lat_center)))  # Conversion en longitude (~111000 mètres par degré, ajusté par la latitude)

        # Calculer les nouvelles latitudes et longitudes pour chaque éolienne du parc
        i = 0
        for row in range(num_rows):
            for col in range(num_cols):
                # Calcul des coordonnées pour chaque éolienne
                lat_offset = (row - (num_rows - 1) / 2) * row_spacing
                lon_offset = (col - (num_cols - 1) / 2) * col_spacing

                new_latitude = lat_center + lat_offset
                new_longitude = lon_center + lon_offset

                windmill = self.windmills[i]
                i += 1
                windmill.set_coordinates(new_latitude, new_longitude)

                latitudes.append(new_latitude)
                longitudes.append(new_longitude)

        windmill_coordinates = np.vstack((latitudes, longitudes)).T

        # Display windmill locations on a 2D plot
        plt.scatter(windmill_coordinates[:, 1], windmill_coordinates[:, 0], color='red', marker='x')
        plt.xlabel('Longitude (°)')
        plt.ylabel('Latitude (°)')
        plt.title('Location of wind turbines in the farm')
        plt.show()

        # Save the figure to the "figures" sub-folder
        current_directory = os.path.dirname(os.path.abspath(__file__))
        current_directory = current_directory.replace("\\WindFarmPlacement\\WindFarm", "")
        file_name = "Wind_turbines_locations.png"
        figure_path = os.path.join(current_directory, "figures", file_name)
        plt.savefig(figure_path)

        return windmill_coordinates
