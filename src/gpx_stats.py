from datetime import datetime
from pathlib import Path
import json

import gpxpy
from geopy.distance import geodesic

HERE = Path(__file__).parents[1]
IN_DIR = HERE / 'input'
OUT_DIR = HERE / 'output'
OUT_DIR.mkdir(exist_ok=True)


def extract_points(file):
    with open(file, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    points = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append(point)

    return points


def calculate_elevation_change(points):
    current_altitude = points[0].elevation
    ascent = 0
    descent = 0

    for point in points[1:]:
        elevation_change = point.elevation - current_altitude
        current_altitude = point.elevation
        if elevation_change >= 0:
            ascent += elevation_change
        else:
            descent -= elevation_change

    return round(ascent), round(descent)


def average_hr(points):
    hr = []
    for point in points:
        for extension_element in point.extensions[0].iter():
            if extension_element.tag.endswith('hr'):
                hr.append(int(extension_element.text))
    return sum(hr) / len(hr)


def calculate_distance(points):
    current_point = points[0]
    distance = 0

    for next_point in points[1:]:
        distance += distance_between_points(current_point, next_point)
        current_point = next_point

    return distance


def distance_between_points(point1, point2):
    p1 = (point1.latitude, point1.longitude)
    p2 = (point2.latitude, point2.longitude)
    return round(geodesic(p1, p2).m, 1)


def elevation_change_between_points(point1, point2):
    return point2.elevation - point1.elevation


def gradient_between_points(point1, point2):
    distance = distance_between_points(point1, point2)
    elevation_change = elevation_change_between_points(point1, point2)
    if distance > 0:
        return round((elevation_change / distance * 100), 1)
    return 0


def time_between_points(point1, point2):
    return (point2.time - point1.time).total_seconds()


def time_for_segment(points):
    return round((points[-1].time - points[0].time).seconds, 2)


def speed_between_points(point1, point2):
    distance = distance_between_points(point1, point2)
    time_delta = time_between_points(point1, point2)
    return round((distance / time_delta * 3.6), 2)


def create_custom_point(point_1, point_2, percent_of_distance=0.5):
    latitude_delta = point_2.latitude - point_1.latitude
    longitude_delta = point_2.longitude - point_1.longitude
    elevation_delta = point_2.elevation - point_1.elevation
    time_delta = point_2.time - point_1.time

    elevation = point_1.elevation + elevation_delta * percent_of_distance
    latitude = point_1.latitude + latitude_delta * percent_of_distance
    longitude = point_1.longitude + longitude_delta * percent_of_distance
    time = point_1.time + time_delta * percent_of_distance

    new_point = gpxpy.gpx.GPXTrackPoint(latitude, longitude, elevation=elevation, time=time)
    new_point.extensions = point_2.extensions
    return new_point


def find_interpolation_point_by_time(point_1, point_2, segment_time, total_time):
    time_delta = time_between_points(point_1, point_2)
    percent_of_distance = 1 - ((total_time - segment_time) / time_delta)

    new_point = create_custom_point(point_1, point_2, percent_of_distance)
    return new_point


def find_interpolation_point(point_1, point_2, segment_distance, total_distance):
    point_distance = distance_between_points(point_1, point_2)
    percent_of_distance = 1 - ((total_distance - segment_distance) / point_distance)

    new_point = create_custom_point(point_1, point_2, percent_of_distance)
    new_total = total_distance - distance_between_points(new_point, point_2)

    lower_limit = segment_distance - 0.5
    upper_limit = segment_distance + 0.5

    while not lower_limit < new_total < upper_limit:
        if new_total < lower_limit:
            point_distance = distance_between_points(new_point, point_2)
            percent_of_distance = 1 - ((segment_distance - new_total) / point_distance)
            new_point = create_custom_point(new_point, point_2, percent_of_distance)
        elif new_total > upper_limit:
            point_distance = distance_between_points(point_1, new_point)
            percent_of_distance = 1 - ((new_total - segment_distance) / point_distance)
            new_point = create_custom_point(point_1, new_point, percent_of_distance)
        new_total = total_distance - distance_between_points(new_point, point_2)
    return new_point


def calculate_gap(ascent, distance, duration):
    ratio = 1000 / distance

    adjusted_ascent = ascent * ratio
    adjusted_duration = duration * ratio

    gap = adjusted_duration

    remaining_ascent = adjusted_ascent % 50
    remaining_reduction = remaining_ascent * 0.9

    if adjusted_ascent > 50:
        gap -= 45
        remaining_reduction = remaining_ascent * 1.2
    if adjusted_ascent > 100:
        gap -= 60
        remaining_reduction = remaining_ascent * 1.5
    if adjusted_ascent > 150:
        gap -= 75
        remaining_reduction = remaining_ascent * 1.8
    if adjusted_ascent > 200:
        gap -= ((adjusted_ascent - 200) % 50) * 90

    return gap - remaining_reduction


def get_points_by_segment_time(points, segment_time):
    segments = []
    current_segment_points = []

    duration = 0
    current_point = points[0]
    current_segment_points.append(current_point)

    for next_point in points[1:]:
        point_duration = (next_point.time - current_point.time).seconds
        duration += point_duration

        if duration < segment_time:
            current_point = next_point
            current_segment_points.append(current_point)
        elif duration == segment_time:
            current_point = next_point
            current_segment_points.append(current_point)
            segments.append(current_segment_points)
            current_segment_points = [current_point]
            duration = 0
        else:
            interpolated_point = find_interpolation_point_by_time(current_point, next_point, segment_time, duration)
            current_segment_points.append(interpolated_point)
            segments.append(current_segment_points)
            current_segment_points = [interpolated_point]
            duration = time_between_points(interpolated_point, next_point)
            current_point = next_point

    segments.append(current_segment_points)
    return segments


def get_points_by_segment_distance(points, segment_distance):
    segments = []
    current_segment_points = []

    distance = 0
    current_point = points[0]
    current_segment_points.append(current_point)

    for next_point in points[1:]:
        point_distance = distance_between_points(current_point, next_point)
        distance += point_distance
        if distance > segment_distance:
            interpolated_point = find_interpolation_point(current_point, next_point, segment_distance, distance)
            current_segment_points.append(interpolated_point)

            segments.append(current_segment_points)
            current_segment_points = [interpolated_point]
            distance = distance_between_points(interpolated_point, next_point)
        current_point = next_point
        current_segment_points.append(current_point)

    segments.append(current_segment_points)
    return segments


def create_geojson(name, points, segment_distance=None, segment_time=None):
    json = {'name': name,
            'stats': {},
            'segments': [],
            'geojson': {'type': 'FeatureCollection',
                        'features': []}
            }

    distance = calculate_distance(points)
    ascent, descent = calculate_elevation_change(points)
    duration = time_for_segment(points)
    hr = average_hr(points)

    json['stats']['distance'] = distance
    json['stats']['ascent'] = ascent
    json['stats']['descent'] = descent
    json['stats']['duration'] = duration
    json['stats']['hr'] = hr
    json['stats']['gap'] = calculate_gap(ascent, distance, duration)
    json['stats']['performance'] = round(((distance/10) + ascent) / duration * 3600)

    if segment_distance:
        segments = get_points_by_segment_distance(points, segment_distance)
    else:
        segments = get_points_by_segment_time(points, segment_time)

    for nr, segment in enumerate(segments):
        print(segment[0])
        distance = calculate_distance(segment)
        ascent, descent = calculate_elevation_change(segment)
        duration = time_for_segment(segment)
        hr = average_hr(segment)
        if duration != 0:
            performance = round(((distance/10) + ascent) / duration * 3600)

            json['segments'].append({'nr': nr,
                                     'distance': distance,
                                     'ascent': ascent,
                                     'descent': descent,
                                     'duration': duration,
                                     'hr': hr,
                                     'gap': calculate_gap(ascent, distance, duration),
                                     'performance': performance})

    distance = 0
    point1 = points[0]
    start_time = point1.time
    for point2 in points[1:]:
        time = point1.time
        duration = (time - start_time).seconds

        feature = {'type': 'Feature',
                   'properties': {'elevation': point1.elevation,
                                  'speed': speed_between_points(point1, point2),
                                  'gradient': gradient_between_points(point1, point2),
                                  'time': datetime.strftime(time, '%Y-%m-%dT%H:%M:%S'),
                                  'duration': duration,
                                  'distance': distance},
                   'geometry': {'type': 'Point',
                                'coordinates': [point1.longitude, point1.latitude]}
                   }
        json['geojson']['features'].append(feature)

        distance += distance_between_points(point1, point2)
        point1 = point2

    return json


def print_segment_analysis(points, segment_size):
    segments = get_points_by_segment_distance(points, segment_size)
    for nr, segment in enumerate(segments):
        distance = calculate_distance(segment)
        ascent, descent = calculate_elevation_change(segment)
        steepness = (ascent + descent) / distance * 100
        steepness = round(steepness, 1)
        print(f'KM {nr+1}: {len(segment)} points, {distance} meters, {ascent} up, {descent} down, {steepness} elevation change')


def process_file(fn, segment_time):
    my_points = extract_points(IN_DIR / f'{fn}.gpx')
    out = create_geojson('test', my_points, segment_time=segment_time)
    with open(OUT_DIR / f'output_{fn}.geojson', 'w') as file:
        file.write(json.dumps(out['geojson']))
    with open(OUT_DIR / f'out_{fn}.json', 'w') as file:
        file.write(json.dumps(out))
    return out
