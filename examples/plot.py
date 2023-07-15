from WindFarmPlacement.windfarmplacement import WindFarmPlacement

import matplotlib.pyplot as plt
import scipy as sp
import numpy as np
import yaml

# Paramètres de test pour la Study Area qui sont pas mal, i.e : début de résultat avec temps de calcul assez court.

if __name__ == '__main__':

    YAML_filename = "plot_weibull.yaml"

    # Load parameters from YAML file
    with open(YAML_filename, 'r') as file:
        parameters = yaml.load(file, Loader=yaml.FullLoader)

    lon_min, lon_max = parameters['lon_min'], parameters['lon_max']
    lat_min, lat_max = parameters['lat_min'], parameters['lat_max']

    precision_lon = int(parameters['precision_lon'])
    precision_lat = int(parameters['precision_lat'])

    study_area = WindFarmPlacement(lon_min, lon_max, lat_min, lat_max, precision_lon, precision_lat)
    study_area.get_wind_history_data_full_threaded(parameters['study_years'], parameters['study_alt'])

    # Affichage des vitesses moyennes du vent
    plt.imshow(study_area.wind_history.wind_mean, extent=[lon_min, lon_max, lat_min, lat_max], aspect='auto')
    plt.colorbar()
    plt.title("Vitesse moyenne du vent (en m/s) 2013-2023")
    plt.xlabel("Longitude (°)")
    plt.ylabel("Latitude (°)")
    plt.show()
    Weibull = study_area.wind_history.get_moment_weibull_factors()

    histogram = study_area.wind_history.wind_histogram[12, 5]
    normed_histogram = histogram/np.sum(histogram)

    x = np.arange(0, 40)

    shape_atlas, scale_atlas = 1.66, 6.39
    weibull_dist_atlas = sp.stats.weibull_min(shape_atlas, scale=scale_atlas)
    pdf_atlas = weibull_dist_atlas.pdf(x)

    shape_fit, scale_fit = 1.414, 3.435
    weibull_dist_fit = sp.stats.weibull_min(shape_fit, scale=scale_fit)
    pdf_fit = weibull_dist_fit.pdf(x)

    shape, scale = Weibull[12, 5]
    print(shape, scale)
    weibull_dist = sp.stats.weibull_min(shape, scale=scale)
    pdf = weibull_dist.pdf(x)

    plt.figure()
    plt.plot(x, pdf_atlas, 'r', label='Weibull atlas')
    plt.plot(x, pdf_fit, 'b', label='Weibull obtenue avec weibull_min.fit()')
    plt.plot(x, pdf, label='Weibull par calcul des moments')
    plt.xlabel("Vitesse du vent (m/s)")
    plt.ylabel("PDF")
    plt.title("Comparaison des PDF des distributions de Weibull")
    plt.legend()
    plt.grid()
    plt.show()