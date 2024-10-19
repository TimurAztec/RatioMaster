from concurrent.futures import ThreadPoolExecutor, as_completed

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
        
        files = request.files.getlist('files')
        wheel_circumference = request.form.get('wheel_circumference', type=int, default=2111)
        
        def process_file(file):
            if file.filename.endswith('.gpx'):
                data = parse_gpx_data(load_gpx(file))
                return calculate_gear_ratio_with_wheel_circumference(calculate_optimal_gear_ratio(data), wheel_circumference)
            return None
        
        optimal_gear_ratios_list = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_file, file) for file in files]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    optimal_gear_ratios_list.append(result)

        avg_gear_ratio = sum(optimal_gear_ratios_list) / len(optimal_gear_ratios_list) if optimal_gear_ratios_list else 0

        return jsonify({
            "optimal_gear_ratios": find_gear_combinations(avg_gear_ratio),
        }), 200

    except Exception as e:
        return "ERROR: {}".format(str(e))