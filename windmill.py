class Windmill:

    def __init__(self, height, cut_in_speed, cut_out_speed, rated_power, rated_wind_speed):
        self.height = height
        self.cut_in = cut_in_speed
        self.cut_out = cut_out_speed
        self.rated_power = rated_power
        self.rated_wind_speed = rated_wind_speed


"""
P = 0, for V < V_cut-in
P = P_rated * (V - V_cut-in)³ / (V_rated - V_cut-in)³, for V_cut-in ≤ V ≤ V_rated
P = P_rated, for V_rated < V < V_cut-out
P = 0, for V ≥ V_cut-out

Where:
P = Power output of the wind turbine
P_rated = Rated power output of the wind turbine (at the rated wind speed)
V = Wind speed
V_cut-in = Cut-in wind speed
V_rated = Rated wind speed
V_cut-out = Cut-out wind speed
"""