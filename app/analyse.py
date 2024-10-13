import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def find_gear_combinations(target_ratio, max_chainring=60, max_sprocket=23):
    combinations = []

    for chainring in range(28, max_chainring + 1):  # Chainring teeth
        for sprocket in range(9, max_sprocket + 1):  # Sprocket teeth
            ratio = chainring / sprocket

            # Check if the ratio is close to the target ratio (allowing for small tolerance)
            if abs(ratio - target_ratio) < 0.01:  # Tolerance of 0.01
                combinations.append((chainring, sprocket))

    return combinations


def calculate_gear_ratio_with_wheel_circumference(current_gear_ratio, wheel_circumference = 2111):
    standard_wheel_circumference = 2111
    distance_per_pedal_revolution = current_gear_ratio * standard_wheel_circumference
    new_gear_ratio = distance_per_pedal_revolution / wheel_circumference

    return new_gear_ratio

def find_average_surface(surfaces):
    surface_values = []
    for surface in surfaces:
        if surface == 'asphalt':
            surface_values.append(1)
        elif surface == 'concrete':
            surface_values.append(0.98)
        elif surface == 'paved':
            surface_values.append(0.97)
        elif surface == 'compacted':
            surface_values.append(0.85)
        elif surface == 'unpaved':
            surface_values.append(0.75)
        elif surface == 'fine_gravel':
            surface_values.append(0.7)
        elif surface == 'gravel':
            surface_values.append(0.66)
        elif surface == 'ground':
            surface_values.append(0.4)
        elif surface == 'grass':
            surface_values.append(0.35)
        elif surface == 'cobblestone':
            surface_values.append(0.25)
        elif surface == 'dirt':
            surface_values.append(0.2)
        elif surface == 'sand':
            surface_values.append(0.1)
        else:
            surface_values.append(1)
    return np.mean(surface_values) if surface_values else 1

def calculate_optimal_gear_ratio(data):
    # Create fuzzy variables
    speed = ctrl.Antecedent(np.arange(0, 60, 1), 'speed')  # Speed in km/h
    slope = ctrl.Antecedent(np.arange(-35, 35, 1), 'slope')  # Slope in percent
    surface = ctrl.Antecedent(np.arange(0, 1, 0.1), 'surface')  # Slope in percent
    gear_ratio = ctrl.Consequent(np.arange(1, 5, 0.05), 'gear_ratio')  # Gear ratio

    # Membership functions for speed
    speed['low'] = fuzz.trimf(speed.universe, [0, 0, 20])
    speed['medium'] = fuzz.trimf(speed.universe, [15, 25, 35])
    speed['high'] = fuzz.trimf(speed.universe, [30, 40, 60])

    surface['bad'] = fuzz.trimf(surface.universe, [0, 0, 0.25])
    surface['medium'] = fuzz.trimf(surface.universe, [0.2, 0.5, 0.75])
    surface['good'] = fuzz.trimf(surface.universe, [0.7, 1, 1])

    total_distance = round(data['total_distance'])
    flat_threshold = total_distance * 0.001
    low_threshold = total_distance * 0.005
    medium_threshold = total_distance * 0.01
    high_threshold = total_distance * 0.015
    step_threshold = total_distance * 0.05

    elevation_gain = ctrl.Antecedent(np.arange(0, high_threshold + 50, 1), 'elevation_gain')
    elevation_gain['flat'] = fuzz.trimf(elevation_gain.universe, [0, 0, flat_threshold])
    elevation_gain['low'] = fuzz.trimf(elevation_gain.universe, [flat_threshold, low_threshold, low_threshold + ((medium_threshold-low_threshold)/2)])
    elevation_gain['medium'] = fuzz.trimf(elevation_gain.universe,
                                          [low_threshold, medium_threshold, medium_threshold + ((high_threshold-medium_threshold)/2)])
    elevation_gain['high'] = fuzz.trimf(elevation_gain.universe,
                                        [medium_threshold, high_threshold, high_threshold + ((step_threshold-high_threshold)/2)])
    elevation_gain['step'] = fuzz.trimf(elevation_gain.universe,
                                        [high_threshold, step_threshold, step_threshold])
    #
    # Membership functions for gear ratio
    gear_ratio['low'] = fuzz.trimf(gear_ratio.universe, [1, 2, 2.5])
    gear_ratio['medium'] = fuzz.trimf(gear_ratio.universe, [2.3, 2.7, 3.2])
    gear_ratio['high'] = fuzz.trimf(gear_ratio.universe, [3, 3.2, 3.5])
    gear_ratio['track'] = fuzz.trimf(gear_ratio.universe, [3.4, 3.6, 4.2])
    #
    # Membership functions for slope
    slope['negative'] = fuzz.trimf(slope.universe, [-35, -10, 0])
    slope['flat'] = fuzz.trimf(slope.universe, [-5, 0, 5])
    slope['positive'] = fuzz.trimf(slope.universe, [0, 10, 35])
    #
    # Define the fuzzy rules
    rules = [
        # Speed and Elevation Gain
        ctrl.Rule(elevation_gain['flat'], gear_ratio['track']),
        ctrl.Rule(elevation_gain['low'], gear_ratio['high']),
        ctrl.Rule(elevation_gain['medium'], gear_ratio['medium']),
        ctrl.Rule(elevation_gain['high'], gear_ratio['low']),
        ctrl.Rule(elevation_gain['step'], gear_ratio['low']),

        ctrl.Rule(speed['low'], gear_ratio['low']),
        ctrl.Rule(speed['medium'], gear_ratio['medium']),
        ctrl.Rule(speed['high'], gear_ratio['high']),
    ]
    # Calculate average slope as a percentage
    avg_slope = np.mean(data["slopes"])
    slope_rules = [
        ctrl.Rule(slope['negative'], gear_ratio['high']),
        ctrl.Rule(slope['flat'], gear_ratio['medium']),
        ctrl.Rule(slope['positive'], gear_ratio['low']),
    ]
    if avg_slope > 1 or avg_slope < -1:
        rules+=slope_rules
    #
    # Calculate average surface
    if data["surfaces"] and len(data["surfaces"]):
        avg_surface = find_average_surface(data["surfaces"])
        surface_rules = [
            ctrl.Rule(surface['bad'], gear_ratio['low']),
            ctrl.Rule(surface['medium'], gear_ratio['medium']),
            ctrl.Rule(surface['good'], gear_ratio['high']),
        ]
        rules += surface_rules
    #

    # Create the control system and simulation
    gear_ratio_ctrl = ctrl.ControlSystem(rules)
    gear_ratio_simulation = ctrl.ControlSystemSimulation(gear_ratio_ctrl)

    # Input values
    gear_ratio_simulation.input['speed'] = data['average_speed']
    gear_ratio_simulation.input['elevation_gain'] = data['elevation_gain']
    if avg_slope > 1 or avg_slope < -1:
        gear_ratio_simulation.input['slope'] = avg_slope
    if data["surfaces"] and len(data["surfaces"]):
        gear_ratio_simulation.input['surface'] = avg_surface

    # Compute the result
    gear_ratio_simulation.compute()

    return gear_ratio_simulation.output['gear_ratio']