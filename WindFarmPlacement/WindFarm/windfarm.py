class WindFarm:

    def __init__(self, target_power, windmills=None, topography=None):
        if windmills is None:
            # Apparemment Pycharm dit que c'est mieux d'écrire comme ça
            self.windmills = windmills
        self.target_power = target_power
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
