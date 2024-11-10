import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def create_surface_fuzzy():
    surface = ctrl.Antecedent(np.arange(0, 1, 0.01), 'surface')
    surface['bad'] = fuzz.trimf(surface.universe, [0, 0, 0.66])
    surface['medium'] = fuzz.trimf(surface.universe, [0.44, 0.77, 0.9])
    surface['good'] = fuzz.trimf(surface.universe, [0.82, 0.96, 1])
    surface['perfect'] = fuzz.trimf(surface.universe, [0.95, 1, 1])
    return surface

def create_elevation_gain_fuzzy(data):
    flat_threshold = data['elevation_flat_threshold']
    low_threshold = data['elevation_low_threshold']
    medium_threshold = data['elevation_medium_threshold']
    high_threshold = data['elevation_high_threshold']
    step_threshold = data['elevation_step_threshold']

    elevation_gain = ctrl.Antecedent(np.arange(0, high_threshold + 50, 1), 'elevation_gain')
    elevation_gain['flat'] = fuzz.trimf(elevation_gain.universe, [0, 0, flat_threshold])
    elevation_gain['low'] = fuzz.trimf(elevation_gain.universe, [flat_threshold, low_threshold, low_threshold + (
                (medium_threshold - low_threshold) / 2)])
    elevation_gain['medium'] = fuzz.trimf(elevation_gain.universe, [low_threshold, medium_threshold,
                                                                    medium_threshold + ((
                                                                                                    high_threshold - medium_threshold) / 2)])
    elevation_gain['high'] = fuzz.trimf(elevation_gain.universe, [medium_threshold, high_threshold, high_threshold + (
                (step_threshold - high_threshold) / 2)])
    elevation_gain['step'] = fuzz.trimf(elevation_gain.universe, [high_threshold, step_threshold, step_threshold])
    return elevation_gain

def create_power_fuzzy():
    power = ctrl.Antecedent(np.arange(0, 500, 1), 'power')
    power['low'] = fuzz.trimf(power.universe, [0, 0, 150])
    power['medium'] = fuzz.trimf(power.universe, [100, 200, 300])
    power['high'] = fuzz.trimf(power.universe, [250, 400, 500])
    return power

def create_speed_threshold():
    speed_threshold = ctrl.Consequent(np.arange(0, 75, 0.1), 'speed')
    speed_threshold['low'] = fuzz.trimf(speed_threshold.universe, [0, 0, 20])
    speed_threshold['medium'] = fuzz.trimf(speed_threshold.universe, [15, 25, 35])
    speed_threshold['high'] = fuzz.trimf(speed_threshold.universe, [30, 35, 45])
    speed_threshold['track'] = fuzz.trimf(speed_threshold.universe, [40, 50, 70])
    return speed_threshold

def create_estimated_speed():
    speed = ctrl.Consequent(np.arange(0, 75, 0.1), 'speed')
    speed['low'] = fuzz.trimf(speed.universe, [0, 0, 15])
    speed['medium'] = fuzz.trimf(speed.universe, [10, 20, 25])
    speed['high'] = fuzz.trimf(speed.universe, [20, 30, 40])
    speed['track'] = fuzz.trimf(speed.universe, [35, 50, 70])
    return speed

def create_speed_fuzzy():
    speed = ctrl.Antecedent(np.arange(0, 70, 0.1), 'speed')
    speed['low'] = fuzz.trimf(speed.universe, [0, 0, 20])
    speed['medium'] = fuzz.trimf(speed.universe, [15, 25, 35])
    speed['high'] = fuzz.trimf(speed.universe, [30, 35, 45])
    speed['track'] = fuzz.trimf(speed.universe, [40, 50, 70])
    return speed

def calculate_optimal_gear_ratio(data):
    speed = create_speed_fuzzy()
    slope = ctrl.Antecedent(np.arange(-35, 35, 0.1), 'slope')
    surface = create_surface_fuzzy()
    cadence = ctrl.Antecedent(np.arange(0, 140, 1), 'cadence')
    heart_rate = ctrl.Antecedent(np.arange(0, 200, 1), 'heart_rate')
    power = create_power_fuzzy()
    gear_ratio = ctrl.Consequent(np.arange(1, 5, 0.05), 'gear_ratio')
    elevation_gain = create_elevation_gain_fuzzy(data)

    cadence['low'] = fuzz.trimf(cadence.universe, [0, 0, 60])
    cadence['medium'] = fuzz.trimf(cadence.universe, [50, 80, 110])
    cadence['high'] = fuzz.trimf(cadence.universe, [100, 130, 140])

    heart_rate['low'] = fuzz.trimf(heart_rate.universe, [0, 0, 120])
    heart_rate['medium'] = fuzz.trimf(heart_rate.universe, [100, 140, 180])
    heart_rate['high'] = fuzz.trimf(heart_rate.universe, [160, 200, 200])

    gear_ratio['low'] = fuzz.trimf(gear_ratio.universe, [1, 2, 2.5])
    gear_ratio['medium'] = fuzz.trimf(gear_ratio.universe, [2.3, 2.7, 3.2])
    gear_ratio['high'] = fuzz.trimf(gear_ratio.universe, [3, 3.2, 3.5])
    gear_ratio['track'] = fuzz.trimf(gear_ratio.universe, [3.4, 3.6, 4.2])

    slope['negative'] = fuzz.trimf(slope.universe, [-35, -10, -5])
    slope['flat'] = fuzz.trimf(slope.universe, [-10, 0, 10])
    slope['positive'] = fuzz.trimf(slope.universe, [5, 10, 35])

    rules = []

    speed_rules = [
        ctrl.Rule(speed['low'] & elevation_gain['flat'] & surface['good'], gear_ratio['medium']),
        ctrl.Rule(speed['low'] & elevation_gain['flat'] & surface['perfect'], gear_ratio['medium']),
        ctrl.Rule(speed['low'] & elevation_gain['low'], gear_ratio['low']),
        ctrl.Rule(speed['low'] & elevation_gain['medium'], gear_ratio['low']),
        ctrl.Rule(speed['low'] & elevation_gain['high'] & surface['bad'], gear_ratio['low']),
        ctrl.Rule(speed['low'] & elevation_gain['step'] & surface['bad'], gear_ratio['low']),

        ctrl.Rule(speed['medium'] & elevation_gain['flat'] & surface['good'], gear_ratio['high']),
        ctrl.Rule(speed['medium'] & elevation_gain['flat'] & surface['perfect'], gear_ratio['high']),
        ctrl.Rule(speed['medium'] & elevation_gain['medium'] & surface['medium'], gear_ratio['medium']),
        ctrl.Rule(speed['medium'] & elevation_gain['high'] & surface['good'], gear_ratio['medium']),
        ctrl.Rule(speed['medium'] & elevation_gain['high'] & surface['bad'], gear_ratio['low']),

        ctrl.Rule(speed['high'] & elevation_gain['flat'] & surface['good'], gear_ratio['high']),
        ctrl.Rule(speed['high'] & elevation_gain['flat'] & surface['perfect'], gear_ratio['track']),
        ctrl.Rule(speed['high'] & elevation_gain['low'] & surface['good'], gear_ratio['medium']),
        ctrl.Rule(speed['high'] & elevation_gain['low'] & surface['perfect'], gear_ratio['high']),
        ctrl.Rule(speed['high'] & surface['bad'], gear_ratio['medium']),
        ctrl.Rule(speed['medium'] & surface['bad'], gear_ratio['low']),
        ctrl.Rule(speed['high'] & elevation_gain['high'] & surface['good'], gear_ratio['high']),
        ctrl.Rule(speed['high'] & elevation_gain['high'] & surface['bad'], gear_ratio['low']),

        ctrl.Rule(speed['high'] & elevation_gain['high'] & surface['bad'], gear_ratio['medium']),
        ctrl.Rule(speed['medium'] & elevation_gain['step'] & surface['bad'], gear_ratio['low']),
        ctrl.Rule(speed['low'] & elevation_gain['high'] & surface['bad'], gear_ratio['low']),

        ctrl.Rule(speed['low'] & elevation_gain['step'] & surface['bad'], gear_ratio['low']),
        ctrl.Rule(speed['medium'] & elevation_gain['high'] & surface['bad'], gear_ratio['medium']),
        ctrl.Rule(speed['high'] & elevation_gain['step'] & surface['bad'], gear_ratio['high'])
    ]
    rules+=speed_rules

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
        ctrl.Rule(surface['perfect'], gear_ratio['track']),
    ]
    rules += surface_rules

    track_surface_rules = [
        ctrl.Rule(surface['perfect'] & elevation_gain['flat'], gear_ratio['track']),
    ]
    rules += track_surface_rules

    cadence_rules = [
        ctrl.Rule(cadence['low'], gear_ratio['low']),
        ctrl.Rule(cadence['medium'], gear_ratio['medium']),
        ctrl.Rule(cadence['high'], gear_ratio['high']),
    ]

    if data['avg_cadence'] > 0:
        rules += cadence_rules

    heart_rate_rules = [
        ctrl.Rule(heart_rate['low'], gear_ratio['low']),
        ctrl.Rule(heart_rate['medium'], gear_ratio['medium']),
        ctrl.Rule(heart_rate['high'], gear_ratio['high']),
    ]

    if data['avg_heart_rate'] > 0:
        rules += heart_rate_rules

    power_rules = [
        ctrl.Rule(power['low'], gear_ratio['low']),
        ctrl.Rule(power['medium'], gear_ratio['medium']),
        ctrl.Rule(power['high'], gear_ratio['high']),
    ]

    if data['avg_power'] > 0:
        rules += power_rules

    gear_ratio_ctrl = ctrl.ControlSystem(rules)
    gear_ratio_simulation = ctrl.ControlSystemSimulation(gear_ratio_ctrl)

    gear_ratio_simulation.input['elevation_gain'] = data['elevation_gain']
    gear_ratio_simulation.input['surface'] = data["avg_surface"]
    gear_ratio_simulation.input['speed'] = data['avg_speed'] if data["avg_speed"] > 0 else data["avg_estimated_speed"]

    if avg_slope > 1 or avg_slope < -1:
        gear_ratio_simulation.input['slope'] = avg_slope
    if data['avg_cadence'] > 0:
        gear_ratio_simulation.input['cadence'] = data['avg_cadence']
    if data['avg_heart_rate'] > 0:
        gear_ratio_simulation.input['heart_rate'] = data['avg_heart_rate']
    if data['avg_power'] > 0:
        gear_ratio_simulation.input['power'] = data['avg_power']

    gear_ratio_simulation.compute()

    return gear_ratio_simulation.output['gear_ratio']


def estimate_speed(data, mode='threshold'):
    surface = create_surface_fuzzy()
    elevation_gain = create_elevation_gain_fuzzy(data)

    if data['avg_power'] > 0:
        power = create_power_fuzzy()

    speed_threshold = create_speed_threshold() if mode == 'threshold' else create_estimated_speed()

    rules = [
        ctrl.Rule(surface['bad'] & elevation_gain['flat'], speed_threshold['high']),
        ctrl.Rule(surface['bad'] & elevation_gain['low'], speed_threshold['medium']),
        ctrl.Rule(surface['bad'] & elevation_gain['medium'], speed_threshold['medium']),
        ctrl.Rule(surface['bad'] & elevation_gain['high'], speed_threshold['low']),
        ctrl.Rule(surface['bad'] & elevation_gain['step'], speed_threshold['low']),

        ctrl.Rule(surface['medium'] & elevation_gain['flat'], speed_threshold['high']),
        ctrl.Rule(surface['medium'] & elevation_gain['low'], speed_threshold['high']),
        ctrl.Rule(surface['medium'] & elevation_gain['medium'], speed_threshold['medium']),
        ctrl.Rule(surface['medium'] & elevation_gain['high'], speed_threshold['low']),
        ctrl.Rule(surface['medium'] & elevation_gain['step'], speed_threshold['low']),

        ctrl.Rule(surface['good'] & elevation_gain['flat'], speed_threshold['track']),
        ctrl.Rule(surface['good'] & elevation_gain['low'], speed_threshold['high']),
        ctrl.Rule(surface['good'] & elevation_gain['medium'], speed_threshold['medium']),
        ctrl.Rule(surface['good'] & elevation_gain['high'], speed_threshold['low']),
        ctrl.Rule(surface['good'] & elevation_gain['step'], speed_threshold['low']),

        ctrl.Rule(surface['perfect'] & elevation_gain['flat'], speed_threshold['track']),
        ctrl.Rule(surface['perfect'] & elevation_gain['low'], speed_threshold['track']),
        ctrl.Rule(surface['perfect'] & elevation_gain['medium'], speed_threshold['high']),
        ctrl.Rule(surface['perfect'] & elevation_gain['high'], speed_threshold['medium']),
        ctrl.Rule(surface['perfect'] & elevation_gain['step'], speed_threshold['low']),
    ]

    if data['avg_power'] > 0:
        rules += [
            ctrl.Rule(power['low'] & surface['good'], speed_threshold['medium']),
            ctrl.Rule(power['medium'] & surface['good'], speed_threshold['medium']),
            ctrl.Rule(power['high'] & surface['good'], speed_threshold['high']),
            ctrl.Rule(power['low'] & surface['perfect'], speed_threshold['medium']),
            ctrl.Rule(power['medium'] & surface['perfect'], speed_threshold['high']),
            ctrl.Rule(power['high'] & surface['perfect'], speed_threshold['track']),
        ]

    speed_control = ctrl.ControlSystem(rules)
    speed_simulation = ctrl.ControlSystemSimulation(speed_control)

    speed_simulation.input['elevation_gain'] = data['elevation_gain']
    speed_simulation.input['surface'] = data["avg_surface"]
    if data['avg_power'] > 0:
        speed_simulation.input['avg_power'] = data["avg_power"]

    speed_simulation.compute()

    return speed_simulation.output.get('speed', 70)

def estimate_average_power(data):
    speed = create_speed_fuzzy()
    surface = create_surface_fuzzy()
    heart_rate = ctrl.Antecedent(np.arange(0, 200, 1), 'heart_rate')
    average_power = ctrl.Consequent(np.arange(0, 500, 1), 'average_power')
    elevation_gain = create_elevation_gain_fuzzy(data)

    heart_rate['low'] = fuzz.trimf(heart_rate.universe, [0, 0, 90])
    heart_rate['medium'] = fuzz.trimf(heart_rate.universe, [70, 120, 150])
    heart_rate['high'] = fuzz.trimf(heart_rate.universe, [130, 200, 200])

    average_power['low'] = fuzz.trimf(average_power.universe, [0, 0, 100])
    average_power['medium'] = fuzz.trimf(average_power.universe, [50, 150, 300])
    average_power['high'] = fuzz.trimf(average_power.universe, [250, 400, 750])

    rules = [
        ctrl.Rule(speed['low'] & surface['bad'], average_power['low']),
        ctrl.Rule(speed['low'] & surface['medium'], average_power['low']),
        ctrl.Rule(speed['low'] & surface['good'], average_power['medium']),
        ctrl.Rule(speed['low'] & surface['perfect'], average_power['medium']),

        ctrl.Rule(speed['medium'] & surface['bad'], average_power['low']),
        ctrl.Rule(speed['medium'] & surface['medium'], average_power['medium']),
        ctrl.Rule(speed['medium'] & surface['good'], average_power['medium']),
        ctrl.Rule(speed['medium'] & surface['perfect'], average_power['high']),

        ctrl.Rule(speed['high'] & surface['bad'], average_power['medium']),
        ctrl.Rule(speed['high'] & surface['medium'], average_power['high']),
        ctrl.Rule(speed['high'] & surface['good'], average_power['high']),
        ctrl.Rule(speed['high'] & surface['perfect'], average_power['high']),

        ctrl.Rule(speed['track'] & surface['bad'], average_power['medium']),
        ctrl.Rule(speed['track'] & surface['medium'], average_power['high']),
        ctrl.Rule(speed['track'] & surface['good'], average_power['high']),
        ctrl.Rule(speed['track'] & surface['perfect'], average_power['high']),

        ctrl.Rule(speed['low'] & elevation_gain['flat'], average_power['low']),
        ctrl.Rule(speed['low'] & elevation_gain['low'], average_power['low']),
        ctrl.Rule(speed['low'] & elevation_gain['medium'], average_power['medium']),
        ctrl.Rule(speed['low'] & elevation_gain['high'], average_power['medium']),
        ctrl.Rule(speed['low'] & elevation_gain['step'], average_power['medium']),

        ctrl.Rule(speed['medium'] & elevation_gain['flat'], average_power['medium']),
        ctrl.Rule(speed['medium'] & elevation_gain['low'], average_power['medium']),
        ctrl.Rule(speed['medium'] & elevation_gain['medium'], average_power['high']),
        ctrl.Rule(speed['medium'] & elevation_gain['high'], average_power['high']),
        ctrl.Rule(speed['medium'] & elevation_gain['step'], average_power['high']),

        ctrl.Rule(speed['high'] & elevation_gain['flat'], average_power['high']),
        ctrl.Rule(speed['high'] & elevation_gain['low'], average_power['high']),
        ctrl.Rule(speed['high'] & elevation_gain['medium'], average_power['high']),
        ctrl.Rule(speed['high'] & elevation_gain['high'], average_power['high']),
        ctrl.Rule(speed['high'] & elevation_gain['step'], average_power['high']),

        ctrl.Rule(speed['track'] & elevation_gain['flat'], average_power['high']),
        ctrl.Rule(speed['track'] & elevation_gain['low'], average_power['high']),
        ctrl.Rule(speed['track'] & elevation_gain['medium'], average_power['high']),
        ctrl.Rule(speed['track'] & elevation_gain['high'], average_power['high']),
        ctrl.Rule(speed['track'] & elevation_gain['step'], average_power['high']),
    ]

    heart_rate_rules = [
        ctrl.Rule(heart_rate['low'], average_power['low']),
        ctrl.Rule(heart_rate['medium'], average_power['medium']),
        ctrl.Rule(heart_rate['high'], average_power['high'])
    ]
    if data['avg_heart_rate'] > 0:
        rules += heart_rate_rules

    power_control = ctrl.ControlSystem(rules)
    power_simulation = ctrl.ControlSystemSimulation(power_control)

    power_simulation.input['speed'] = data['avg_speed']
    power_simulation.input['surface'] = data['avg_surface']
    power_simulation.input['elevation_gain'] = data['elevation_gain']

    if data['avg_heart_rate'] > 0:
        power_simulation.input['heart_rate'] = data['avg_heart_rate']

    power_simulation.compute()

    return power_simulation.output.get('average_power', 122)