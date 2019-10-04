import haversine
from math import sin, cos, atan2, acos, radians, degrees, sqrt, fabs


def avg(l):
    assert len(l) > 0

    return sum(l) / float(len(l))


# Returns array of diffs between current and previous element for a given numeric array
def calculate_diffs(l):
    assert len(l) > 0

    diffs = []
    last_num = l[0]
    for num in l:
        diffs.append(num - last_num)
        last_num = num

    return diffs


# Returns array of diffs between current and previous element for a given numeric array
def calculate_time_diffs(l):
    assert len(l) > 0

    diffs = []
    last_ts = l[0]
    for ts in l:
        diffs.append(get_timedelta_micros(ts, last_ts))
        last_ts = ts

    return diffs


# Returns string with standard stats for array - min, max, avg. Filtering out zero values
def get_numeric_array_stats_without_zeros(l):
    without_zeros = list(filter(lambda x: x != 0.0, l))
    return "Min: %.5f, Max: %.5f, Avg: %.5f" % (min(without_zeros), max(without_zeros), avg(without_zeros))


def get_timedelta_micros(time1, time2):
    time_delta = time1 - time2
    return time_delta.seconds * 1000000 + time_delta.microseconds


# Calculates haversine dist between two TrackPoint or Coords objects
def get_dist(point1, point2):
    return haversine.haversine(
        (point1.lat, point1.lon),
        (point2.lat, point2.lon)
    )


EARTH_RADIUS = 6371.0088


# Calculates bearing in degrees from point to point
def get_bearing(coords1, coords2):
    lat1, lon1, lat2, lon2 = map(radians, (coords1.lat, coords1.lon, coords2.lat, coords2.lon))

    y = sin(lon2 - lon1) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2 - lon1)

    return (degrees(atan2(y, x)) + 360) % 360


def get_2d_bearing(coords1, coords2):
    """Calculates 2d bearing of vectors in terms of 2d space"""
    x1, y1, x2, y2 = coords1.lat, coords1.lon, coords2.lat - coords1.lat, coords2.lon - coords1.lon
    return (degrees(acos((x1 * x2 + y1 * y2) / (sqrt(x1 * x1 + y1 * y1) * sqrt(x2 * x2 + y2 * y2)))) + 360) % 360


def get_bearing_diff(bearing1, bearing2):
    """Consider the least of two bearings"""
    d1 = bearing2 - bearing1
    d2 = bearing2 + 360 - bearing1  # Like if we stepped over 360 degree mark
    d3 = bearing2 - bearing1 - 360
    if fabs(d1) <= fabs(d2) and fabs(d1) <= fabs(d3):
        return d1
    elif fabs(d2) <= fabs(d3):
        return d2
    else:
        return d3


def sign(x):
    if x < 0:
        return -1
    elif x > 0:
        return 1
    else:
        return 0


def print_tracks_stats(tracks):
    print("Total %d tracks" % len(tracks))
    for i in range(len(tracks)):
        print("%d:" % i)
        tracks[i].print_stats()


