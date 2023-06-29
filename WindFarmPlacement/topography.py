import requests
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os


class ElevationData:
    def __init__(self, lon_min, lon_max, lat_min, lat_max, num_lon_points, num_lat_points):
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.num_lon_points = num_lon_points
        self.num_lat_points = num_lat_points
        self.elevation_array = np.zeros((num_lat_points, num_lon_points))

    def retrieve_elevation_data(self):
        """Function that uses the Open Elevation API to get elevation data points from a specified lat/long reactangular region.

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
        return self.elevation_array
    
    def calculate_flatness_score(self):
        """Function that calculates a flatness score from an elevation array. A higher score means the surface is flatter.

        :param : 
        :type :
        :return:
        :rtype :
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

    def plot_3d_surface_map(self,area_id):
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
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Plot the surface
        ax.plot_surface(X, Y, self.elevation_array, cmap='viridis')

        # Set labels and title
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_zlabel('Elevation (m)')
        ax.set_title('3D Surface Map of Elevation')

        # Show the plot
        plt.show()

        # Save the figure to the "figures" sub-folder
        current_directory = os.path.dirname(os.path.abspath(__file__))
        current_directory = current_directory.replace("\\WindFarmPlacement", "")
        file_name = "topography_map_" + str(area_id) + ".png"
        figure_path = os.path.join(current_directory, "figures", file_name)
        plt.savefig(figure_path)

# # Example usage in mountains s=39
# lon_min, lon_max = -124.75, -124.0
# lat_min, lat_max = 50.75, 51
# num_lon_points = 10
# num_lat_points = 10

# # Example usage in everest s=27
# lon_min, lon_max = 86.75, 87
# lat_min, lat_max = 27.75, 28
# num_lon_points = 10
# num_lat_points = 10

# # Example usage in prairies s=95
# lon_min, lon_max = -106.75, -105.75
# lat_min, lat_max = 50.5, 49.5
# num_lon_points = 10
# num_lat_points = 10

"""
# Example usage in ocean s=100
lon_min, lon_max = -127.0, -126.0
lat_min, lat_max = 47.0, 48.0
num_lon_points = 10
num_lat_points = 10

# Retreive elevation data and calculate score
elevation_data = ElevationData(lon_min, lon_max, lat_min, lat_max, num_lon_points, num_lat_points)
elevation_data.retrieve_elevation_data()
elevation_data.calculate_flatness_score()

# Store elevation data and score
elevation_array = elevation_data.get_elevation_array()
flatness_score = elevation_data.flatness_score

# Plot elevation data
elevation_data.plot_3d_surface_map()
# Print results
print(f"Flatness score = ",flatness_score)
"""


