from geopy.distance import geodesic


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
    return round(sum(hr) / len(hr))


def calculate_distance(points):
    current_point = points[0]
    distance = 0

    for next_point in points[1:]:
        distance += distance_between_points(current_point, next_point)
        current_point = next_point

    return round(distance)


def distance_between_points(point1, point2):
    p1 = (point1.latitude, point1.longitude)
    p2 = (point2.latitude, point2.longitude)
    return round(geodesic(p1, p2).m, 1)


def gradient_between_points(point1, point2):
    distance = distance_between_points(point1, point2)
    elevation_change = _elevation_change_between_points(point1, point2)
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


def _elevation_change_between_points(point1, point2):
    return point2.elevation - point1.elevation
