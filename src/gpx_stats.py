from datetime import datetime
from pathlib import Path
import json

import gpxpy

from src.performance_tools import calculate_gap
from src.metrics import (calculate_elevation_change,
                         average_hr,
                         calculate_distance,
                         distance_between_points,
                         gradient_between_points,
                         time_between_points,
                         time_for_segment,
                         speed_between_points)
from src.gpx_adjustments import (find_interpolation_point_by_time,
                                 find_interpolation_point)

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
    elevation = [point.elevation for point in points]

    json['stats']['distance'] = distance
    json['stats']['ascent'] = ascent
    json['stats']['descent'] = descent
    json['stats']['duration'] = duration
    json['stats']['hr'] = hr
    json['stats']['gap'] = calculate_gap(ascent, distance, duration)
    json['stats']['performance'] = round(((distance/10) + ascent) / duration * 3600)
    json['stats']['vam'] = ascent / descent * 3600
    json['stats']['elevation'] = elevation

    if segment_distance:
        segments = get_points_by_segment_distance(points, segment_distance)
    else:
        segments = get_points_by_segment_time(points, segment_time)

    for nr, segment in enumerate(segments):
        distance = calculate_distance(segment)
        ascent, descent = calculate_elevation_change(segment)
        duration = time_for_segment(segment)
        hr = average_hr(segment)
        elevation = [point.elevation for point in segment]
        if duration != 0:
            performance = round(((distance/10) + ascent) / duration * 3600)

            json['segments'].append({'nr': nr,
                                     'distance': distance,
                                     'ascent': ascent,
                                     'descent': descent,
                                     'duration': duration,
                                     'hr': hr,
                                     'gap': calculate_gap(ascent, distance, duration),
                                     'performance': performance,
                                     'vam': ascent / duration * 3600,
                                     'elevation': elevation})
    for k in json['segments'][0].keys():
        json[k] = [entry[k] for entry in json['segments']]

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


def analyze_course_profile(points, segment_size):
    segments = get_points_by_segment_distance(points, segment_size)
    result = {'segments': []}
    for nr, segment in enumerate(segments):
        distance = calculate_distance(segment)
        ascent, descent = calculate_elevation_change(segment)
        steepness = (ascent + descent) / distance * 100
        steepness = round(steepness, 1)
        elevation = [point.elevation for point in segment]
        result['segments'].append({'label': nr+1,
                                   'distance': distance,
                                   'ascent': ascent,
                                   'descent': descent,
                                   'steepness': steepness,
                                   'elevation': elevation})

    for k in result['segments'][0].keys():
        if k == 'elevation':
            result[k] = [elevation for entry in result['segments'] for elevation in entry[k]]
            elevation_labels = []
            for i, entry in enumerate(result['segments']):
                for elevation in entry[k]:
                    elevation_labels.append(i)
            result['elevation_label'] = elevation_labels
        else:
            result[k] = [entry[k] for entry in result['segments']]
    return result


def process_performance_file(fn, segment_time=None, segment_distance=None):
    my_points = extract_points(IN_DIR / f'{fn}.gpx')
    if segment_time:
        out = create_geojson(fn, my_points, segment_time=segment_time)
    elif segment_distance:
        out = create_geojson(fn, my_points, segment_distance=segment_distance)
    else:
        raise Exception("Invalid function call.")
    with open(OUT_DIR / f'output_performance_{fn}.geojson', 'w') as file:
        file.write(json.dumps(out['geojson']))
    with open(OUT_DIR / f'out_performance_{fn}.json', 'w') as file:
        file.write(json.dumps(out))
    return out


def process_course_file(fn, distance=1000):
    my_points = extract_points(IN_DIR / f'{fn}.gpx')
    out = analyze_course_profile(my_points, distance)
    with open(OUT_DIR / f'out_profile_{fn}.json', 'w') as file:
        file.write(json.dumps(out))
    return out
