import numpy as np
import scipy as sp

from math import pi


class Windmill:

    def __init__(self, height, blade_length, cut_in_speed=3, cut_out_speed=25):
        self.height = height
        self.blade_length = blade_length
        self.cut_in = cut_in_speed
        self.cut_out = cut_out_speed

    def theoretical_power(self, wind_data):
        """Fonction qui calcule la puissance théorique du vent qu'une éolienne doit pouvoir atteindre pour chaque
        coordonnée d'une grille en fonction des mesures du vent passées en paramètre. Les formules, méthodes et
        hypothèses proviennent de la source suivante : https://eolienne.f4jr.org/eolienne_etude_theorique

        :param wind_data : Objet WindHistory qui contient les données sur les mesures historiques du vent de la zone
        d'étude. Contient, la valeur moyenne du vent et la distribution des classes de vent (histogramme).
        :type wind_data : WindHistory
        :return: Retourne une matrice contenant la puissance théorique pouvant être produite
        :rtype : numpy.array
        """

        # Dans un premier temps on simplifie en considérant les paramètres atmosphériques constants et identiques en
        # tout point. Des mesures sur ses paramètres permettraient d'améliorer l'estimation.
        To = 288.15  # Kelvin
        Po = 101.3e3  # Pascal
        R = 287  # J/kg.K
        rho = Po/(R*To)  # kg/m^3

        # Calcul de la surface couvert par l'éolienne
        surface = pi*self.blade_length**2

        # Calcul des facteurs de forme et d'échelle de la distribution de Weibull pour les vitesses du vent.
        weibull = wind_data.weibull()
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
                power_matrix[x, y] = np.sum((0.5*rho*surface*winds**3)*proba)

        # Limite de Bertz sur le rendement éolien. Le vent conserve de l'énergie et n'est pas stoppé par l'éolienne.
        bertz_coefficient = 16 / 27
        power_matrix *= bertz_coefficient

        # Limite supplémentaire liés rendements des transformations d'énergie
        power_matrix *= 0.7

        return power_matrix
