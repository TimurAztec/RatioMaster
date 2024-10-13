import gpxpy
import requests
import numpy as np

def load_gpx(file):
    return gpxpy.parse(file)

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371e3  # Radius of the Earth in meters
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
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


def get_surface_types(coordinates):
    if not coordinates:
        return []

    # Find the min and max latitude and longitude for the bounding box
    latitudes = [coord[0] for coord in coordinates]
    longitudes = [coord[1] for coord in coordinates]

    min_lat = min(latitudes)
    max_lat = max(latitudes)
    min_lon = min(longitudes)
    max_lon = max(longitudes)

    # Create an Overpass API query using the bounding box
    query = f"""
    [out:json];
    (
      way({min_lat},{min_lon},{max_lat},{max_lon})["surface"];
    );
    out body;
    """

    # Make the API request
    response = requests.get("http://overpass-api.de/api/interpreter", params={'data': query})

    if response.status_code != 200:
        raise Exception("Error fetching data from Overpass API")

    data = response.json()
    surfaces = []

    # Map surface types to their corresponding coordinates
    for element in data.get('elements', []):
        if 'tags' in element and 'surface' in element['tags']:
            surface_type = element['tags']['surface']
            surfaces.append(surface_type)

    return surfaces

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
                        previous_point.latitude, previous_point.longitude,
                        point.latitude, point.longitude
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

    surfaces = get_surface_types(coordinates)

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

