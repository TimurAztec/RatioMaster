import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

from app import app
from flask import request, render_template, jsonify

from app.analyse import calculate_optimal_gear_ratio, find_gear_combinations, calculate_gear_ratio_with_wheel_circumference
from app.gpx import load_gpx, parse_gpx_data


@app.route('/', methods=['GET'])
def render_index():
    try:
        return render_template("index.html")
    except Exception as e:
        return "ERROR: {}".format(str(e))

@app.route('/upload_gpx', methods=['POST'])
def upload_gpx_files():
    try:
        if 'files' not in request.files:
            raise ValueError("No selected files!")

        files = request.files.getlist('files')  # Retrieve the list of files
        wheel_circumference = request.form.get('wheel_circumference', type=int, default=2111)
        for file in files:
            if file.filename.endswith('.gpx'):
                data = parse_gpx_data(load_gpx(file))
                data['wheel_circumference'] = 2286
                # data['fixed_gear'] = True
                # data['average_power'] = 200
                optimal_gear_ratios = find_gear_combinations(calculate_gear_ratio_with_wheel_circumference(calculate_optimal_gear_ratio(data), wheel_circumference))
        return jsonify({
                    "optimal_gear_ratios": optimal_gear_ratios
                }), 200
    except Exception as e:
        return "ERROR: {}".format(str(e))