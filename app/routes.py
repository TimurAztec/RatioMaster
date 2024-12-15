from app import app
from flask import request, render_template, jsonify, abort
from app.analyse import analyze_data

@app.route('/', methods=['GET'])
def render_index():
    try:
        return render_template("index.html")
    except Exception as e:
        return "ERROR: {}".format(str(e))


@app.route('/upload', methods=['POST'])
async def upload_gpx_files():
    try:
        if 'files' not in request.files and 'links' not in request.form:
            raise ValueError("No selected files or links!")

        files = request.files.getlist('files')
        links = request.form.getlist('links')
        wheel_circumference = request.form.get('wheel_circumference', type=int, default=2111)
        weight = request.form.get('weight', type=int, default=None)
        crank_length = request.form.get('crank_length', type=int, default=170)
        ride_style = request.form.get('ride_style', type=str, default=None)
        fixed_gear = request.form.get('fixed_gear', type=bool, default=None)
        flat_pedals = request.form.get('flat_pedals', type=bool, default=None)
        lang = request.form.get('lang', type=str, default="en")

        return jsonify(await analyze_data(
            {
                "files": files,
                "links": links,
                "wheel_circumference": wheel_circumference,
                "weight": weight,
                "crank_length": crank_length,
                "ride_style": ride_style,
                "fixed_gear": fixed_gear,
                "flat_pedals": flat_pedals,
                "lang": lang
            })), 200

    except Exception as e:
        return abort(400, str(e))