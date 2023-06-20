from matplotlib import pyplot as plt

class FlatZoneFinder:
    def __init__(self, elevation_data):
        self.elevation_data = elevation_data
        self.flat_zones = []
        self.good_zones = []

    def find_flat_zones(self, lat_min, lat_max, lon_min, lon_max):
        self.flat_zones = []
        elevation_array = self.elevation_data.get_elevation_array()
        for i in range(len(elevation_array)):
            for j in range(len(elevation_array[0])):
                lat = lat_min + i * (lat_max - lat_min) / (len(elevation_array) - 1)
                lon = lon_min + j * (lon_max - lon_min) / (len(elevation_array[0]) - 1)
                flatness_score = self.elevation_data.calculate_flatness_score(lat, lon)
                if flatness_score > 90:  # Seuil à ajuster au besoin
                    self.flat_zones.append((lat, lon))

    def is_flat_zone(self, lat, lon):
        flatness_score = self.elevation_data.calculate_flatness_score(lat, lon)
        return flatness_score > 90  # Seuil à ajuster au besoin

    def check_spacing(self, lat_min, lat_max, lon_min, lon_max, num_windmills, turbine_diam):
        self.good_zones = []
        vertical_spacing = 5 * turbine_diam
        horizontal_spacing = 5 * turbine_diam

        for zone in self.flat_zones:
            lat, lon = zone
            if lat + vertical_spacing <= lat_max and lon + horizontal_spacing <= lon_max:
                self.good_zones.append((lat, lon))

    def plot_windmills_on_3d_map(self, num_windmills):
        self.elevation_data.plot_3d_surface_map()
        for zone in self.good_zones[:num_windmills]:
            lat, lon = zone
            elevation = self.elevation_data.get_elevation(lat, lon)
            plt.plot(lon, lat, elevation, 'ro')
        plt.show()