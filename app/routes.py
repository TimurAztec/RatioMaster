import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np

from app import app
from flask import request, render_template, jsonify, abort
from strava2gpx import strava2gpx
from app.analyse import calculate_optimal_gear_ratio, find_gear_combination, calculate_gear_ratio_with_wheel_circumference
from app.gpx import load_gpx, parse_gpx_data
from dotenv import load_dotenv
import aiofiles

load_dotenv()
STRAVA_API_KEY = os.getenv('STRAVA_API_KEY')

@app.route('/', methods=['GET'])
def render_index():
    try:
        return render_template("index.html")
    except Exception as e:
        return "ERROR: {}".format(str(e))


@app.route('/upload_gpx', methods=['POST'])
async def upload_gpx_files():
    try:
        if 'files' not in request.files and 'links' not in request.form:
            raise ValueError("No selected files or links!")

        files = request.files.getlist('files')
        links = request.form.getlist('links')
        wheel_circumference = request.form.get('wheel_circumference', type=int, default=2111)

        strava_gpx_api = strava2gpx(client_id=138004, client_secret='d994095b0ef52c46f328460ee4d321396729b335', refresh_token='d5c5809884a46f6fcad1a7ddb422bf79ec9eedf5')
        await strava_gpx_api.connect()

        def process_file(file):
            if file.filename.endswith('.gpx'):
                data = parse_gpx_data(load_gpx(file))  # Implement your GPX parsing logic
                return {
                    "data": data,
                    "gear_ratio": calculate_gear_ratio_with_wheel_circumference(calculate_optimal_gear_ratio(data),
                                                                     wheel_circumference)
                }
            return None

        async def fetch_gpx_from_strava(link):
            activity_id = extract_activity_id(link)  # You need to implement this function
            output_filename = f"{activity_id}.gpx"
            await strava_gpx_api.write_to_gpx(activity_id, output=output_filename)

            async with aiofiles.open(output_filename, 'r') as f:
                gpx_data = await f.read()

            return parse_gpx_data(gpx_data)  # Implement your GPX parsing logic

        data = []

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_file, file) for file in files]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    data.append(result)

        for link in links:
            try:
                gpx_data = await fetch_gpx_from_strava(link)
                result = calculate_gear_ratio_with_wheel_circumference(calculate_optimal_gear_ratio(gpx_data),
                                                                       wheel_circumference)
                data.append(result)
            except Exception as e:
                print(f"Error processing link {link}: {e}")

        avg_gear_ratio = np.mean(np.array([obj["gear_ratio"] for obj in data]))
        avg_speed = np.array([obj["data"]["avg_speed"] for obj in data])
        avg_heart_rates = np.array([obj["data"]["avg_heart_rate"] for obj in data])
        avg_cadences = np.array([obj["data"]["avg_cadence"] for obj in data])
        avg_powers = np.array([obj["data"]["avg_power"] for obj in data])
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

        avg_data = {
            "avg_speed": np.mean(avg_speed),
            "avg_heart_rate": np.mean(avg_heart_rates),
            "avg_cadence": np.mean(avg_cadences),
            "avg_power": np.mean(avg_powers),
            "avg_surface": np.mean(avg_surfaces),
            "elevation_gain": np.mean(elevation_gains),
            "elevation_threshold": np.mean(elevation_thresholds),
        }

        return jsonify({
            "optimal_gear_ratio": find_gear_combination(avg_gear_ratio),
            "data": avg_data
        }), 200

    except Exception as e:
        return abort(400, str(e))

def extract_activity_id(link):
    match = re.search(r"activities/(\d+)", link)
    if match:
        return match.group(1)
    raise ValueError("Invalid Strava link format")