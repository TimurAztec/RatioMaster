import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def find_gear_combination(target_ratio, max_chainring=60, max_sprocket=23):
    combinations = []

    for chainring in range(28, max_chainring + 1):
        for sprocket in range(9, max_sprocket + 1):
            ratio = chainring / sprocket

            if abs(ratio - target_ratio) < 0.01:
                combinations.append((chainring, sprocket))


    return combinations[-1]


def calculate_gear_ratio_with_wheel_circumference(current_gear_ratio, wheel_circumference = 2111):
    standard_wheel_circumference = 2111
    distance_per_pedal_revolution = current_gear_ratio * standard_wheel_circumference
    new_gear_ratio = distance_per_pedal_revolution / wheel_circumference

    return new_gear_ratio

def calculate_optimal_gear_ratio(data):
    speed = ctrl.Antecedent(np.arange(0, 60, 1), 'speed')
    slope = ctrl.Antecedent(np.arange(-35, 35, 1), 'slope')
    surface = ctrl.Antecedent(np.arange(0, 1, 0.1), 'surface')
    gear_ratio = ctrl.Consequent(np.arange(1, 5, 0.05), 'gear_ratio')

    speed['low'] = fuzz.trimf(speed.universe, [0, 0, 20])
    speed['medium'] = fuzz.trimf(speed.universe, [15, 25, 35])
    speed['high'] = fuzz.trimf(speed.universe, [30, 40, 60])

    surface['bad'] = fuzz.trimf(surface.universe, [0, 0, 0.66])
    surface['medium'] = fuzz.trimf(surface.universe, [0.44, 0.77, 0.9])
    surface['good'] = fuzz.trimf(surface.universe, [0.82, 1, 1])

    flat_threshold = data['elevation_flat_threshold']
    low_threshold = data['elevation_low_threshold']
    medium_threshold = data['elevation_medium_threshold']
    high_threshold = data['elevation_high_threshold']
    step_threshold = data['elevation_step_threshold']

    elevation_gain = ctrl.Antecedent(np.arange(0, high_threshold + 50, 1), 'elevation_gain')
    elevation_gain['flat'] = fuzz.trimf(elevation_gain.universe, [0, 0, flat_threshold])
    elevation_gain['low'] = fuzz.trimf(elevation_gain.universe, [flat_threshold, low_threshold, low_threshold + ((medium_threshold-low_threshold)/2)])
    elevation_gain['medium'] = fuzz.trimf(elevation_gain.universe,
                                          [low_threshold, medium_threshold, medium_threshold + ((high_threshold-medium_threshold)/2)])
    elevation_gain['high'] = fuzz.trimf(elevation_gain.universe,
                                        [medium_threshold, high_threshold, high_threshold + ((step_threshold-high_threshold)/2)])
    elevation_gain['step'] = fuzz.trimf(elevation_gain.universe,
                                        [high_threshold, step_threshold, step_threshold])

    gear_ratio['low'] = fuzz.trimf(gear_ratio.universe, [1, 2, 2.5])
    gear_ratio['medium'] = fuzz.trimf(gear_ratio.universe, [2.3, 2.7, 3.2])
    gear_ratio['high'] = fuzz.trimf(gear_ratio.universe, [3, 3.2, 3.5])
    gear_ratio['track'] = fuzz.trimf(gear_ratio.universe, [3.4, 3.6, 4.2])

    slope['negative'] = fuzz.trimf(slope.universe, [-35, -10, -5])
    slope['flat'] = fuzz.trimf(slope.universe, [-10, 0, 10])
    slope['positive'] = fuzz.trimf(slope.universe, [5, 10, 35])

    rules = [
        ctrl.Rule(elevation_gain['flat'], gear_ratio['track']),
        ctrl.Rule(elevation_gain['low'], gear_ratio['high']),
        ctrl.Rule(elevation_gain['medium'], gear_ratio['medium']),
        ctrl.Rule(elevation_gain['high'], gear_ratio['low']),
        ctrl.Rule(elevation_gain['step'], gear_ratio['low']),

        ctrl.Rule(speed['low'], gear_ratio['low']),
        ctrl.Rule(speed['medium'], gear_ratio['medium']),
        ctrl.Rule(speed['high'], gear_ratio['high']),
    ]

    avg_slope = np.mean(data["slopes"])
    slope_rules = [
        ctrl.Rule(slope['negative'], gear_ratio['high']),
        ctrl.Rule(slope['flat'], gear_ratio['medium']),
        ctrl.Rule(slope['positive'], gear_ratio['low']),
    ]
    if avg_slope > 1 or avg_slope < -1:
        rules+=slope_rules

    surface_rules = [
        ctrl.Rule(surface['bad'], gear_ratio['low']),
        ctrl.Rule(surface['medium'], gear_ratio['medium']),
        ctrl.Rule(surface['good'], gear_ratio['high']),
    ]
    rules += surface_rules

    gear_ratio_ctrl = ctrl.ControlSystem(rules)
    gear_ratio_simulation = ctrl.ControlSystemSimulation(gear_ratio_ctrl)

    gear_ratio_simulation.input['speed'] = data['avg_speed']
    gear_ratio_simulation.input['elevation_gain'] = data['elevation_gain']
    gear_ratio_simulation.input['surface'] = data["avg_surface"]
    if avg_slope > 1 or avg_slope < -1:
        gear_ratio_simulation.input['slope'] = avg_slope

    gear_ratio_simulation.compute()

    return gear_ratio_simulation.output['gear_ratio']