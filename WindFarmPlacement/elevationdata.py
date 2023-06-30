import requests
import numpy as np
import matplotlib.pyplot as plt
import os


class ElevationData:
    """Objet conceptuel représentant les caractéristiques topographiques d'une zone d'étude.

    :param lon_min: La longitude minimale de la zone d'intérêt.
    :type lon_min: float
    :param lon_max: La longitude maximale de la zone d'intérêt.
    :type lon_max: float
    :param lat_min: La latitude minimale de la zone d'intérêt.
    :type lat_min: float
    :param lat_max: La latitude maximale de la zone d'intérêt.
    :type lat_max: float
    :param num_lon_points: Le nombre de points de longitude pour l'échantillonnage de la zone.
    :type num_lon_points: int
    :param num_lat_points: Le nombre de points de latitude pour l'échantillonnage de la zone.
    :type num_lat_points: int

    """

    def __init__(self, lon_min, lon_max, lat_min, lat_max, num_lon_points, num_lat_points):
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.num_lon_points = num_lon_points
        self.num_lat_points = num_lat_points
        self.elevation_array = np.zeros((num_lat_points, num_lon_points))

    def retrieve_elevation_data(self):
        """Fonction qui utilise l'API d'Open Elevation pour récupérer les données d'élévation de la zone pour chaque
        couple de coordonnées de longitudes et de latitudes.

        :param : 
        :type :
        :return:
        :rtype :

        """
        lon_step = (self.lon_max - self.lon_min) / (self.num_lon_points - 1)
        lat_step = (self.lat_max - self.lat_min) / (self.num_lat_points - 1)

        for i in range(self.num_lat_points):
            for j in range(self.num_lon_points):
                lon = self.lon_min + j * lon_step
                lat = self.lat_min + i * lat_step
                url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
                response = requests.get(url)
                data = response.json()
                elevation = data["results"][0]["elevation"]
                self.elevation_array[i, j] = elevation

    def get_elevation_array(self):
        """Fonction qui retourne le tableau des données d'élévation.

        :return: Le tableau bidimensionnel contenant les données d'élévation.
        :rtype: numpy.ndarray

        """

        return self.elevation_array
    
    def calculate_flatness_score(self):
        """Fonction qui calcule le score de planéité pour les données d'élévation.
        Le score de planéité est basé sur l'écart-type des valeurs d'élévation.

        :return: Le score de planéité des données d'élévation.
        :rtype: float

        """

        # Calculate the standard deviation of the elevation values
        std_dev = np.std(self.elevation_array)

        # Handle the case when standard deviation is zero
        if std_dev == 0.0:
            self.flatness_score = 100.0
        else:
            # Normalize the standard deviation to a value between 0 and 1 using 1000 as a reference std around mount Everest
            normalized_std_dev = std_dev / 1000.0

            # Map the normalized standard deviation to a score between 0 and 100
            self.flatness_score = (1 - normalized_std_dev) * 100.0

    def plot_3d_surface_map(self, area_id):
        """Function that plots a 3D surface map from an elevation array and a lat/lon grid.

        :param : 
        :type :
        :return:
        :rtype :

        """

        # Create meshgrid for x and y coordinates
        x = np.linspace(self.lon_min, self.lon_max, self.num_lon_points)
        y = np.linspace(self.lat_min, self.lat_max, self.num_lat_points)
        X, Y = np.meshgrid(x, y)

        # Create a 3D figure
        ax = plt.axes(projection='3d')

        # Plot the surface
        ax.plot_surface(X, Y, self.elevation_array, cmap='viridis')

        # Set labels and title
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_zlabel('Elevation (m)')

        # Création d'un FixedLocator
        ax.xaxis.set_major_locator(plt.FixedLocator(x, nbins=5))
        ax.yaxis.set_major_locator(plt.FixedLocator(y, nbins=5))

        # Formattage des repères des axes avec plusieurs décimales
        ax.xaxis.set_major_formatter(plt.FixedFormatter(x.round(4)))
        ax.yaxis.set_major_formatter(plt.FixedFormatter(y.round(4)))

        ax.set_title('3D Surface Map of Elevation')

        # Save the figure to the "figures" sub-folder
        current_directory = os.path.dirname(os.path.abspath(__file__))
        current_directory = current_directory.replace("\\WindFarmPlacement", "")
        file_name = "topography_map_" + str(area_id) + ".png"
        figure_path = os.path.join(current_directory, "figures", file_name)
        plt.savefig(figure_path)

        # Show the plot
        plt.show()


