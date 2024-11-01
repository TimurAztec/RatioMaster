import re
import os
from strava2gpx import strava2gpx
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from app.fuzzy import calculate_optimal_gear_ratio, estimate_speed_threshold, estimate_average_power
from app.gpx import load_gpx, parse_gpx_data
from dotenv import load_dotenv
import aiofiles

load_dotenv()
STRAVA_API_KEY = os.getenv('STRAVA_API_KEY')


def find_gear_combination(target_ratio, max_chainring=60, max_sprocket=28, threshold=0.01):
    combinations = []

    for chainring in range(28, max_chainring + 1):
        for sprocket in range(9, max_sprocket + 1):
            ratio = chainring / sprocket

            if abs(ratio - target_ratio) < threshold:
                combinations.append((chainring, sprocket))

    return combinations[-1] if len(combinations) else find_gear_combination(target_ratio, threshold=threshold+0.01)


def calculate_gear_ratio_with_wheel_circumference(current_gear_ratio, wheel_circumference=2111):
    standard_wheel_circumference = 2111
    distance_per_pedal_revolution = current_gear_ratio * standard_wheel_circumference
    new_gear_ratio = distance_per_pedal_revolution / wheel_circumference

    return new_gear_ratio


def extract_activity_id(link):
    match = re.search(r"activities/(\d+)", link)
    if match:
        return match.group(1)
    raise ValueError("Invalid Strava link format")


async def analyze_data(input_data):
    strava_gpx_api = strava2gpx(client_id=138004, client_secret='d994095b0ef52c46f328460ee4d321396729b335',
                                refresh_token='d5c5809884a46f6fcad1a7ddb422bf79ec9eedf5')
    await strava_gpx_api.connect()

    def process_file(file):
        if file.filename.endswith('.gpx'):
            data = parse_gpx_data(load_gpx(file))
            data["speed_threshold"] = estimate_speed_threshold(data)
            data["avg_estimated_power"] = estimate_average_power(data)
            return {
                "data": data,
                "gear_ratio": calculate_gear_ratio_with_wheel_circumference(calculate_optimal_gear_ratio(data),
                                                                            input_data["wheel_circumference"])
            }
        return None

    async def fetch_gpx_from_strava(link):
        activity_id = extract_activity_id(link)
        output_filename = f"{activity_id}.gpx"
        await strava_gpx_api.write_to_gpx(activity_id, output=output_filename)

        async with aiofiles.open(output_filename, 'r') as f:
            gpx_data = await f.read()

        return parse_gpx_data(gpx_data)

    data = []

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_file, file) for file in input_data["files"]]
        for future in as_completed(futures):
            result = future.result()
            if result:
                data.append(result)

    for link in input_data["links"]:
        try:
            gpx_data = await fetch_gpx_from_strava(link)
            result = calculate_gear_ratio_with_wheel_circumference(calculate_optimal_gear_ratio(gpx_data),
                                                                   input_data["wheel_circumference"])
            data.append(result)
        except Exception as e:
            print(f"Error processing link {link}: {e}")

    avg_gear_ratio = np.mean(np.array([obj["gear_ratio"] for obj in data]))
    avg_speed = np.array([obj["data"]["avg_speed"] for obj in data])
    avg_speed_thresholds = np.array([obj["data"]["speed_threshold"] for obj in data])
    avg_heart_rates = np.array([obj["data"]["avg_heart_rate"] for obj in data])
    avg_cadences = np.array([obj["data"]["avg_cadence"] for obj in data])
    avg_powers = np.array([obj["data"]["avg_power"] for obj in data])
    avg_estimated_powers = np.array([obj["data"]["avg_estimated_power"] for obj in data])
    avg_surfaces = np.array([obj["data"]["avg_surface"] for obj in data])
    elevation_gains = []
    elevation_thresholds = []
    for obj in data:
        elevation_gains.append(obj["data"]["elevation_gain"])
        obj_elevation_threshold = (
            obj["data"]["elevation_high_threshold"]
            if obj["data"]["elevation_gain"] < obj["data"]["elevation_high_threshold"]
            else obj["data"]["elevation_step_threshold"]
        )
        elevation_thresholds.append(obj_elevation_threshold)

    avg_power = np.mean(avg_powers)
    if avg_power == 0:
        avg_power = np.mean(avg_estimated_powers)

    avg_data = {
        "avg_speed": np.mean(avg_speed),
        "avg_speed_threshold": np.mean(avg_speed_thresholds),
        "avg_heart_rate": np.mean(avg_heart_rates),
        "avg_cadence": np.mean(avg_cadences),
        "avg_power": avg_power,
        "avg_surface": np.mean(avg_surfaces),
        "elevation_gain": np.mean(elevation_gains),
        "elevation_threshold": np.mean(elevation_thresholds),
    }

    return {
        "optimal_gear_ratio": find_gear_combination(avg_gear_ratio),
        "data": avg_data
    }
