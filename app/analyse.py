import re
import os
import openai
from strava2gpx import strava2gpx
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from app.fuzzy import calculate_optimal_gear_ratio, estimate_speed, estimate_average_power
from app.gps import parse_gpx_data, parse_tcx_data
from dotenv import load_dotenv
import aiofiles
from openai import AsyncOpenAI

load_dotenv()
STRAVA_API_KEY = os.getenv('STRAVA_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openaiClient = AsyncOpenAI(
  api_key=OPENAI_API_KEY
)

def find_gear_combination(target_ratio, max_chainring=60, max_sprocket=28, threshold=0.01):
    best_combination = None
    max_skid_patches = 0

    def gcd(a, b):
        return a if b == 0 else gcd(b, a % b)

    for chainring in range(28, max_chainring + 1):
        for sprocket in range(9, max_sprocket + 1):
            ratio = chainring / sprocket
            if abs(ratio - target_ratio) < threshold:
                skid_patches = sprocket / gcd(chainring, sprocket)
                if skid_patches > max_skid_patches:
                    max_skid_patches = skid_patches
                    best_combination = (chainring, sprocket)

    return best_combination if best_combination else find_gear_combination(target_ratio, threshold=threshold + 0.01)


def calculate_gear_ratio_with_adjustments(current_gear_ratio, wheel_circumference=2111, crank_length=170):
    standard_wheel_circumference = 2111  # in mm
    standard_crank_length = 170  # in mm, typical crank length
    distance_per_pedal_revolution = current_gear_ratio * standard_wheel_circumference
    adjusted_distance_per_pedal_revolution = distance_per_pedal_revolution * (crank_length / standard_crank_length)

    new_gear_ratio = adjusted_distance_per_pedal_revolution / wheel_circumference

    return new_gear_ratio


def extract_activity_id(link):
    match = re.search(r"activities/(\d+)", link)
    if match:
        return match.group(1)
    raise ValueError("Invalid Strava link format")

async def get_gear_ratio_explanation(avg_data, optimal_gear_ratio, wheel_circumference=2111, lang="en"):
    if lang == "ua":
        language_instruction = "Будь ласка, поясніть на українській мові"
    elif lang == "en":
        language_instruction = "Please explain in English"
    else:
        language_instruction = f"Please explain in {lang}"

    prompt = (
        f"{language_instruction} the rationale for selecting a gear ratio of {round(optimal_gear_ratio, 2)} based on the following data:\n"
        f"- Wheel circumference: {round(wheel_circumference)} mm\n"
        f"- Surface quality: {round(avg_data['avg_surface'], 2)} (scale 0 to 1)\n"
        f"- Elevation gain: {round(avg_data['elevation_gain'])} meters\n"
    )

    if avg_data.get('avg_power') and avg_data['avg_power'] > 0:
        prompt += f"- Power: {round(avg_data['avg_power'])} watts\n"

    if avg_data.get('avg_speed') and avg_data['avg_speed'] > 0:
        prompt += f"- Speed: {round(avg_data['avg_speed'], 1)} km/h\n"

    if avg_data.get('avg_estimated_speed') and avg_data['avg_estimated_speed'] > 0:
        prompt += f"- Suggested avg speed: {round(avg_data['avg_estimated_speed'], 1)} km/h\n"

    if avg_data.get('avg_heart_rate') and avg_data['avg_heart_rate'] > 0:
        prompt += f"- Heart rate: {round(avg_data['avg_heart_rate'])} bpm\n"

    if avg_data.get('avg_cadence') and avg_data['avg_cadence'] > 0:
        prompt += f"- Cadence: {round(avg_data['avg_cadence'])} rpm\n"

    prompt += (
        "Provide a clear, structured, and detailed explanation of how these factors influenced the gear ratio choice. "
        "Please propose the most suitable bike type and riding conditions based on the data, assuming all bikes are single-speed/fixed-gear. "
        "Use the following guidelines to identify the bike type: \n"
        "- If surface quality is above 0.95 and the gear ratio exceeds 3.2, it suggests a track bike ride.\n"
        "- If surface quality is above 0.77 and the gear ratio exceeds 2.5, it indicates a single-speed road bike ride.\n"
        "- If surface quality is below 0.77, it likely means off-road riding.\n"
        "- If surface quality is below 0.5, it likely indicates a single-speed MTB or gravel bike ride.\n"
        "- If the wheel circumference is above 2300 mm, it usually indicates a 29\" MTB bike.\n"
        "- Wheel sizes 28\" generally indicate a road or track bike.\n"
        "- Wheel sizes 29\", 27.5\", and 26\" generally indicate an MTB bike.\n"
        "- For MTB bikes, surface quality should also be low (below 0.5) for an accurate classification.\n"
        "- Ensure that your reasoning accounts for both surface quality and gear ratio in identifying the bike type."
        "Explain your reasoning as if you made the gear ratio decision, and do not include any numerical data. "
        "Focus entirely on the logic behind your selection."
    )

    try:
        response = await openaiClient.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that explains single-speed bike gear ratio decisions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=333,
            temperature=0.2
        )
        explanation = response.choices[0].message.content.strip()

        if not explanation or explanation.endswith(('.', '!', '?')):
            return explanation

        return explanation + "."

    except openai._exceptions.RateLimitError:
        print("Quota limit exceeded or rate limit error")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

async def analyze_data(input_data):
    strava_gpx_api = strava2gpx(client_id=138004, client_secret='d994095b0ef52c46f328460ee4d321396729b335',
                                refresh_token='d5c5809884a46f6fcad1a7ddb422bf79ec9eedf5')
    await strava_gpx_api.connect()

    def process_file(file):
        if file.filename.endswith('.gpx'):
            data = parse_gpx_data(file)
        if file.filename.endswith('.tcx'):
            data = parse_tcx_data(file)
        if data:
            data["avg_estimated_speed"] = estimate_speed(data, mode='estimate') if not data["avg_speed"] else 0
            data["speed_threshold"] = estimate_speed(data, mode='threshold')
            data["avg_estimated_power"] = estimate_average_power(data) if not data["avg_power"] and data["avg_speed"] else 0
            return {
                "data": data,
                "gear_ratio": calculate_gear_ratio_with_adjustments(calculate_optimal_gear_ratio(data),
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
            result = calculate_gear_ratio_with_adjustments(calculate_optimal_gear_ratio(gpx_data),
                                                                   input_data["wheel_circumference"])
            data.append(result)
        except Exception as e:
            print(f"Error processing link {link}: {e}")

    avg_gear_ratio = np.mean(np.array([obj["gear_ratio"] for obj in data]))
    avg_speeds = np.array([obj["data"]["avg_speed"] for obj in data])
    avg_speed_thresholds = np.array([obj["data"]["speed_threshold"] for obj in data])
    avg_heart_rates = np.array([obj["data"]["avg_heart_rate"] for obj in data])
    avg_cadences = np.array([obj["data"]["avg_cadence"] for obj in data])
    avg_powers = np.array([obj["data"]["avg_power"] for obj in data])
    avg_estimated_powers = np.array([obj["data"]["avg_estimated_power"] for obj in data])
    avg_estimated_speeds = np.array([obj["data"]["avg_estimated_speed"] for obj in data])
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
    avg_speed = np.mean(avg_speeds)
    avg_power = np.mean(avg_powers) if len(avg_powers) else 0
    if avg_power == 0 and avg_speed > 0:
        avg_power = np.mean(avg_estimated_powers)

    avg_data = {
        "avg_speed": avg_speed if avg_speed > 0 else np.mean(avg_estimated_speeds),
        "avg_speed_threshold": np.mean(avg_speed_thresholds),
        "avg_heart_rate": np.mean(avg_heart_rates),
        "avg_cadence": np.mean(avg_cadences),
        "avg_power": avg_power,
        "avg_surface": np.mean(avg_surfaces),
        "elevation_gain": np.mean(elevation_gains),
        "elevation_threshold": np.mean(elevation_thresholds),
    }

    explanation = await get_gear_ratio_explanation(avg_data, avg_gear_ratio, input_data["wheel_circumference"], input_data["lang"])
    return {
        "optimal_gear_ratio": find_gear_combination(avg_gear_ratio),
        "data": avg_data,
        "explanation": explanation
    }
