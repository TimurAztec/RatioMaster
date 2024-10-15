import gpxpy
import requests
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_gpx(file):
    return gpxpy.parse(file)

def calculate_distance(coord1, coord2):
    R = 6371000
    lat1, lon1 = np.radians(coord1)
    lat2, lon2 = np.radians(coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c

def calculate_air_density(altitude):
    rho0 = 1.225
    scale_height = 8500

    air_density = rho0 * np.exp(-altitude / scale_height)

    return air_density

def calculate_power(speed, slope, altitude, total_weight=75, drag_coefficient=0.88, frontal_area=0.5, rolling_resistance_coefficient=0.004):
    air_density = calculate_air_density(altitude)
    gravity = 9.81
    slope_radians = np.arctan(slope / 100.0)
    power_gravity = total_weight * gravity * np.sin(slope_radians) * speed
    power_aero = 0.5 * air_density * drag_coefficient * frontal_area * (speed ** 3)
    power_rolling = total_weight * gravity * rolling_resistance_coefficient * speed
    total_power = power_gravity + power_aero + power_rolling

    return total_power

def calculate_elevation_gain(elevations):
    total_gain = 0
    previous_elevation = elevations[0]

    for current_elevation in elevations[1:]:
        if current_elevation > previous_elevation:
            total_gain += current_elevation - previous_elevation

        previous_elevation = current_elevation

    return total_gain


def filter_close_coordinates(coordinates, threshold_distance=25):
    if not coordinates:
        return []

    filtered_coords = [coordinates[0]]  # Keep the first coordinate

    for coord in coordinates[1:]:
        last_coord = filtered_coords[-1]
        if calculate_distance(last_coord, coord) > threshold_distance:
            filtered_coords.append(coord)

    return filtered_coords

def map_surface_value(surface):
    if surface == 'asphalt':
        return 1
    elif surface == 'concrete':
        return 1
    elif surface == 'chipseal':
        return 1
    elif surface == 'concrete:plates':
        return 0.9
    elif surface == 'sett':
        return 0.9
    elif surface == 'paving_stones':
        return 0.9
    elif surface == 'bricks':
        return 0.85
    elif surface == 'paved':
        return 1
    elif surface == 'compacted':
        return 0.65
    elif surface == 'unpaved':
        return 0.6
    elif surface == 'fine_gravel':
        return 0.66
    elif surface == 'gravel':
        return 0.5
    elif surface == 'pebblestone':
        return 0.3
    elif surface == 'rock':
        return 0.01
    elif surface == 'ground':
        return 0.3
    elif surface == 'grass':
        return 0.2
    elif surface == 'unhewn_cobblestone':
        return 0.13
    elif surface == 'cobblestone':
        return 0.15
    elif surface == 'dirt':
        return 0.1
    elif surface == 'mud':
        return 0.1
    elif surface == 'sand':
        return 0.1
    else:
        return 1

def map_highway_value(highway):
    if highway == 'motorway':
        return 1.0
    elif highway == 'trunk':
        return 0.9
    elif highway == 'primary':
        return 1
    elif highway == 'secondary':
        return 0.9
    elif highway == 'tertiary':
        return 0.75
    elif highway == 'residential':
        return 0.95
    elif highway == 'service':
        return 0.6
    elif highway == 'track':
        return 0.5
    elif highway == 'path':
        return 0.3
    elif highway == 'cycleway':
        return 1
    elif highway == 'footway':
        return 0.3
    elif highway == 'unclassified':
        return 0.5
    else:
        return 1

def map_tracktype_value(tracktype):
    if tracktype == 'grade1':
        return 0.9
    elif tracktype == 'grade2':
        return 0.666
    elif tracktype == 'grade3':
        return 0.333
    elif tracktype == 'grade4':
        return 0.25
    elif tracktype == 'grade5':
        return 0
    else:
        return 0


def process_element(element, coordinates, max_distance):
    # Get element coordinates
    element_coords = None
    if 'center' in element:
        element_coords = (element['center']['lat'], element['center']['lon'])
    elif 'geometry' in element:
        element_coords = (element['geometry'][0]['lat'], element['geometry'][0]['lon'])

    if not element_coords:
        return None

    is_near = any(calculate_distance(coord, element_coords) <= max_distance for coord in coordinates)

    if not is_near:
        return None  # Skip element if it's too far

    score = 0
    tag_count = 0

    if 'tags' in element:
        tags = element['tags']

        if 'tracktype' in tags:
            tracktype_value = map_tracktype_value(tags['tracktype'])
            score += tracktype_value
            tag_count += 1

        if 'surface' in tags:
            surface_value = map_surface_value(tags['surface'])
            score += surface_value
            tag_count += 1

    if tag_count > 0:
        score /= tag_count
        return score

    return None


def get_surface_types(coordinates, max_distance=100, max_workers=4):
    if not coordinates:
        return []

    latitudes = [coord[0] for coord in coordinates]
    longitudes = [coord[1] for coord in coordinates]

    min_lat = min(latitudes)
    max_lat = max(latitudes)
    min_lon = min(longitudes)
    max_lon = max(longitudes)

    query = f"""
    [out:json];
    (
      way({min_lat},{min_lon},{max_lat},{max_lon})["surface"];
    );
    out body geom;
    """  # Added 'geom' to retrieve geometry for distance calculations

    response = requests.get("http://overpass-api.de/api/interpreter", params={'data': query})

    if response.status_code != 200:
        raise Exception("Error fetching data from Overpass API")

    data = response.json()
    elements = data.get('elements', [])

    results = []

    # Use ThreadPoolExecutor to parallelize the processing of elements
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_element = {
            executor.submit(process_element, element, coordinates, max_distance): element
            for element in elements
        }

        for future in as_completed(future_to_element):
            score = future.result()
            if score is not None:
                results.append(score)

    return results

def parse_gpx_data(gpx_data):
    elevations = []
    distances = []
    slopes = []
    speeds = []
    heart_rates = []
    cadences = []
    powers = []
    coordinates = []

    previous_point = None

    for track in gpx_data.tracks:
        for segment in track.segments:
            for point in segment.points:
                # Append elevation
                elevations.append(point.elevation)
                coordinates.append((point.latitude, point.longitude))

                # Add optional attributes if they exist and are not None or empty
                if hasattr(point, 'speed') and point.speed is not None:
                    speeds.append(point.speed)
                if hasattr(point, 'heart_rate') and point.heart_rate is not None:
                    heart_rates.append(point.heart_rate)
                if hasattr(point, 'cadence') and point.cadence is not None:
                    cadences.append(point.cadence)
                if hasattr(point, 'power') and point.power is not None:
                    powers.append(point.power)

                if previous_point is not None:
                    # Calculate distance between two points using coordinates
                    distance = calculate_distance(
                        (previous_point.latitude, previous_point.longitude),
                        (point.latitude, point.longitude)
                    )
                    distances.append(distance)

                    # Calculate slope (elevation change / horizontal distance)
                    elevation_change = point.elevation - previous_point.elevation
                    if distance > 0:  # Avoid division by zero
                        slope = (elevation_change / distance) * 100  # Slope in percentage
                        slopes.append(slope)

                    # Calculate time difference in seconds
                    time_difference = (point.time - previous_point.time).total_seconds()

                    # Calculate speed only if time difference is greater than 0
                    if time_difference > 0:
                        speed_mps = distance / time_difference  # Speed in meters per second
                        speed_kmh = speed_mps * 3.6  # Convert to kilometers per hour
                        speeds.append(speed_kmh)  # Append calculated speed (km/h)

                        # Estimate power if power meter data is not available
                        if not hasattr(point, 'power') or point.power is None:
                            power_estimated = calculate_power(speed_mps, slope, point.elevation)
                            powers.append(power_estimated)
                    else:
                        speeds.append(0)  # No time difference means speed cannot be calculated

                # Set the current point as the previous point for the next iteration
                previous_point = point

    surfaces = get_surface_types(filter_close_coordinates(coordinates))

    return {
        "elevations": elevations,
        "distances": distances,
        "slopes": slopes,
        "speeds": speeds,
        "heart_rates": heart_rates,
        "cadences": cadences,
        "powers": powers,
        "surfaces": surfaces,
        "total_distance": sum(distances) if distances else 0,
        "elevation_gain": calculate_elevation_gain(elevations) if elevations else 0,
        "average_speed": np.mean(speeds) if speeds else 0,
        "average_heart_rate": np.mean(heart_rates) if heart_rates else 0,
        "average_cadence": np.mean(cadences) if cadences else 0,
        "average_power": np.mean(powers) if powers else 0,
    }

