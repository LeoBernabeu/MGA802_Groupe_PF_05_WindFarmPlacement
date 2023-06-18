from math import pi
import numpy as np
import scipy as sp


class Windmill:

    def __init__(self, height, blade_length, cut_in_speed=0, cut_out_speed=0, rated_power=0, rated_wind_speed=0):
        self.height = height
        self.blade_length = blade_length
        self.cut_in = cut_in_speed
        self.cut_out = cut_out_speed
        self.rated_power = rated_power
        self.rated_wind_speed = rated_wind_speed

    def power(self, wind_speed):
        """All speed are in m/s
        Source https://www.hindawi.com/journals/jen/2016/8519785/)
        """

        # Prise en compte de la hauteur de l'éolienne. Le vent est mesuré à environ 10 mètres au dessus du sol.
        speed = wind_speed*()

        if self.cut_in <= wind_speed <= self.rated_wind_speed:
            power = self.rated_power * (wind_speed - self.cut_in)**3
            power = power/(self.rated_wind_speed - self.cut_in)**3
        elif self.rated_wind_speed < wind_speed < self.cut_out:
            power = self.rated_power
        else:
            power = 0
        return power

    def theoretical_power(self, wind_data):
        """Compute... 1/2*rho*S*V^3 """

        To = 288.15  # Kelvin
        Po = 101.3e3  # Pascal
        R = 287  # J/kg.K
        rho = Po/(R*To)  # Au final avoir les données de température seraient utiles
        surface = pi*self.blade_length**2

        # Prise en compte de la probabilité des vitesses du vent avec Weibull
        weibull = wind_data.weibull()
        winds = np.arange(0, 30.01, 0.01)
        size_x, size_y = np.shape(weibull)[:-1]
        power_matrix = np.zeros((size_x, size_y))
        for x in range(size_x):
            for y in range(size_y):
                shape, scale = weibull[x, y]
                weibull_dist = sp.stats.weibull_min(shape, scale=scale)
                cdf = weibull_dist.cdf(winds)
                proba = np.array([cdf[k]-cdf[k-1] for k in range(len(winds))])
                power_matrix[x, y] = np.sum((0.5*rho*surface*winds**3)*proba)

        # Limite de Bertz
        bertz_coef = 16 / 27
        power_matrix *= bertz_coef

        # Limite supplémentaire à cause des différents rendements : https://eolienne.f4jr.org/eolienne_etude_theorique
        power_matrix *= 0.7

        return power_matrix
