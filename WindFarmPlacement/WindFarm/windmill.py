import numpy as np
import scipy as sp

from math import pi


class Windmill:
    """Objet représentant une éolienne.

    :param height: Hauteur de l'éolienne.
    :type height: float
    :param blade_length: Longueur des pales de l'éolienne.
    :type blade_length: float
    :param cut_in_speed: Vitesse de démarrage de l'éolienne (vitesse minimale pour laquelle elle produit de l'énergie).
    :type cut_in_speed: float
    :param cut_out_speed: Vitesse de coupure de l'éolienne (vitesse maximale à laquelle elle cesse de produire de l'énergie).
    :type cut_out_speed: float

    """

    def __init__(self, height, blade_length, cut_in_speed=3, cut_out_speed=25):
        self.height = height
        self.blade_length = blade_length
        self.cut_in = cut_in_speed
        self.cut_out = cut_out_speed
        self.lat, self.lon = None, None
        self.work_state = False

    def set_coordinates(self, lat, lon):
        """Fonction qui définit les coordonnées géographiques de l'éolienne.

        :param lat: Latitude de l'emplacement de l'éolienne.
        :type lat: float
        :param lon: Longitude de l'emplacement de l'éolienne.
        :type lon: float

        """

        self.lat = lat
        self.lon = lon

    def produced_power(self, wind):
        """Fonction qui calcule la puissance produite par l'éolienne en fonction de la vitesse du vent.

        :param wind: Vitesse du vent.
        :type wind: float
        :return: Puissance produite par l'éolienne.
        :rtype: float

        """

        # Dans un premier temps on simplifie en considérant les paramètres atmosphériques constants et identiques en
        # tout point. Des mesures sur ses paramètres permettraient d'améliorer l'estimation.
        To = 288.15  # Kelvin
        Po = 101.3e3  # Pascal
        R = 287  # J/kg.K
        rho = Po/(R*To)  # kg/m^3

        # Calcul de la surface couvert par l'éolienne
        surface = pi*self.blade_length**2

        power = (0.5 * rho * surface * wind ** 3)

        # Limite de Bertz sur le rendement éolien. Le vent conserve de l'énergie et n'est pas stoppé par l'éolienne.
        bertz_coefficient = 16 / 27
        power *= bertz_coefficient

        # Limite supplémentaire liés rendements des transformations d'énergie
        power *= 0.7

        return power

    def theoretical_power(self, weibull):
        """Fonction qui calcule la puissance théorique du vent qu'une éolienne doit pouvoir atteindre pour chaque
        coordonnée d'une grille en fonction des mesures du vent passées en paramètre. Les formules, les méthodes et les
        hypothèses proviennent de la source suivante : https://eolienne.f4jr.org/eolienne_etude_theorique

        :param weibull: Tableau qui contient les facteurs de forme et d'échelle des distributions de Weibull du vent pour chaque couple de coordonnées de longitudes et de latitudes de la zone étudiée.
        :type weibull: numpy.ndarray
        :return: Retourne une matrice contenant la puissance théorique pouvant être produite.
        :rtype: numpy.array

        """

        size_x, size_y = np.shape(weibull)[:-1]
        power_matrix = np.zeros((size_x, size_y))
        # On crée un échantillonnage à utiliser pour la suite avec la fonction de répartition de Weibull
        winds = np.arange(0, 30.01, 0.01)

        # weibull_min ne peut pas être utilisé de manière vectorielle. On procède donc à l'aide de boucles.
        for x in range(size_x):
            for y in range(size_y):
                shape, scale = weibull[x, y]
                # On calcule la distribution à l'aide des facteurs de forme et d'échelle
                weibull_dist = sp.stats.weibull_min(shape, scale=scale)

                # On calcule la fonction de répartition (Cumulative Distribution Function -> cdf)
                cdf = weibull_dist.cdf(winds)

                # On calcule la probabilité d'occurrence des vitesses de vents.
                proba = np.array([cdf[k]-cdf[k-1] for k in range(len(winds))])

                # Enfin on calcule la puissance maximale pouvant être produite
                power_matrix[x, y] = np.sum(self.produced_power(winds)*proba)

        return power_matrix

    def theorical_power_tuple_weibull_factors(self, shape, scale):
        """Fonction qui calcule la puissance théorique du vent qu'une éolienne doit pouvoir atteindre pour des valeurs
        particulières de facteur de forme et d'échelle d'une distribution de Weibull.

        :param shape: Le facteur de forme d'une distribution de Weibull.
        :type shape: float
        :param scale: Le facteur d'échelle d'une distribution de Weibull.
        :type scale: float
        :return: La puissance théorique.
        :rtype: float

        """

        # On calcule la distribution à l'aide des facteurs de forme et d'échelle
        weibull_dist = sp.stats.weibull_min(shape, scale=scale)

        winds = np.arange(0, 30.01, 0.01)
        # On calcule la fonction de répartition (Cumulative Distribution Function -> cdf)
        cdf = weibull_dist.cdf(winds)

        # On calcule la probabilité d'occurrence des vitesses de vents.
        proba = np.array([cdf[k] - cdf[k - 1] for k in range(len(winds))])

        # Enfin on calcule la puissance maximale pouvant être produite
        power = np.sum(self.produced_power(winds) * proba)

        return power
