import matplotlib.pyplot as plt
import numpy as np


class WindFarm:

    def __init__(self, target_power, windmills=None, topography=None):
        self.target_power = target_power
        if windmills is None:
            # Apparemment Pycharm dit que c'est mieux d'écrire comme ça
            self.windmills = []
        self.topography = topography

    def add_windmill(self, windmill):
        self.windmills.append(windmill)

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

    def place_windmills(self, area_of_interest):
        print(area_of_interest)
        num_windmills = len(self.windmills)

        lat_min, lat_max = area_of_interest[0]
        lon_min, lon_max = area_of_interest[1]

        # Calculer le pas en latitude et en longitude pour les sections
        lat_step = (lat_max - lat_min) / num_windmills
        lon_step = (lon_max - lon_min) / num_windmills

        # Tableau pour stocker les coordonnées des éoliennes
        windmill_coordinates = np.zeros((num_windmills, 2))
        print(lat_min+lat_step, lon_min+lon_step)
        print(windmill_coordinates)

        windmill = self.windmills[0]
        windmill.set_coordinates(lat_min + lat_step, lon_min + lon_step)
        windmill_coordinates[0] = [lat_min+lat_step, lon_min+lon_step]

        # Placer les éoliennes dans chaque petite section
        for i in range(num_windmills):

            # Coordonnées de l'éolienne au milieu de la section
            lat_center = lat_min + (i + 0.5) * lat_step
            lon_center = lon_min + (i + 0.5) * lon_step

            windmill = self.windmills[i]
            rotor_diameter = windmill.blade_length  # Espacement de 5 fois le diamètre (à définir par l'utilisateur)
            # Convertir l'espacement en mètres en coordonnées en lat/long
            distance = 5 * rotor_diameter
            lat_offset = distance / 111000  # Conversion en latitude (~111000 mètres par degré)
            lon_offset = distance / (111000 * np.cos(np.radians(lat_center)))  # Conversion en longitude (~111000 mètres par degré, ajusté par la latitude)

            # Coordonnées de la prochaine éolienne
            lat_center += lat_offset
            lon_center += lon_offset

            windmill.set_coordinates(lat_center, lon_center)
            windmill_coordinates[i] = [lat_center, lon_center]

        # Display windmill locations on a 2D plot
        plt.scatter(windmill_coordinates[:, 1], windmill_coordinates[:, 0], color='red', marker='x')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Windmill Locations')
        plt.show()

        return windmill_coordinates
