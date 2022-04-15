import gpxpy

from src.metrics import (distance_between_points,
                         time_between_points)


def find_interpolation_point_by_time(point_1, point_2, segment_time, total_time):
    time_delta = time_between_points(point_1, point_2)
    percent_of_distance = 1 - ((total_time - segment_time) / time_delta)

    new_point = _create_custom_point(point_1, point_2, percent_of_distance)
    return new_point


def find_interpolation_point(point_1, point_2, segment_distance, total_distance):
    point_distance = distance_between_points(point_1, point_2)
    percent_of_distance = 1 - ((total_distance - segment_distance) / point_distance)

    new_point = _create_custom_point(point_1, point_2, percent_of_distance)
    new_total = total_distance - distance_between_points(new_point, point_2)

    lower_limit = segment_distance - 0.5
    upper_limit = segment_distance + 0.5

    while not lower_limit < new_total < upper_limit:
        if new_total < lower_limit:
            point_distance = distance_between_points(new_point, point_2)
            percent_of_distance = 1 - ((segment_distance - new_total) / point_distance)
            new_point = _create_custom_point(new_point, point_2, percent_of_distance)
        elif new_total > upper_limit:
            point_distance = distance_between_points(point_1, new_point)
            percent_of_distance = 1 - ((new_total - segment_distance) / point_distance)
            new_point = _create_custom_point(point_1, new_point, percent_of_distance)
        new_total = total_distance - distance_between_points(new_point, point_2)
    return new_point


def _create_custom_point(point_1, point_2, percent_of_distance=0.5):
    latitude_delta = point_2.latitude - point_1.latitude
    latitude = point_1.latitude + latitude_delta * percent_of_distance

    longitude_delta = point_2.longitude - point_1.longitude
    longitude = point_1.longitude + longitude_delta * percent_of_distance

    elevation_delta = point_2.elevation - point_1.elevation
    elevation = point_1.elevation + elevation_delta * percent_of_distance

    if point_1.time and point_2.time:
        time_delta = point_2.time - point_1.time
        time = point_1.time + time_delta * percent_of_distance
    else:
        time = None

    new_point = gpxpy.gpx.GPXTrackPoint(latitude, longitude, elevation=elevation, time=time)
    new_point.extensions = point_2.extensions
    return new_point
