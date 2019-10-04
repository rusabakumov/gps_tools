from collections import namedtuple

TrackNormalizationParams = namedtuple('TrackNormalizationParams', ['align_to_minutes', 'neighbor_weights'])

DEFAULT_TRACK_NORMALIZATION_PARAMS = TrackNormalizationParams(align_to_minutes=False, neighbor_weights=None)


def normalize_minute_starts(points):
    from gpstools.track.track import TrackPoint
    if len(points) > 0 and (points[0].time.second != 0 or points[0].time.microsecond > 0):
        new_time = points[0].time.replace(second=0, microsecond=0)
        start_point = TrackPoint(
            new_time,
            points[0].lat,
            points[0].lon,
            points[0].altitude,
            points[0].speed,
            points[0].bearing
        )
        points.insert(0, start_point)

    return points


def normalize_by_neighbor_weights(points, neighbor_weights):
    from gpstools.track.track import TrackPoint
    new_points = []

    prev_point = points[0]
    for i, point in enumerate(points):
        next_point = points[i + 1] if i < len(points) - 1 else points[i]

        new_points.append(TrackPoint(
            time=point.time,
            lat=neighbor_weights[0] * prev_point.lat +
                     neighbor_weights[1] * point.lat + neighbor_weights[2] * next_point.lat,
            lon=neighbor_weights[0] * prev_point.lon +
                     neighbor_weights[1] * point.lon + neighbor_weights[2] * next_point.lon,
            altitude=neighbor_weights[0] * prev_point.altitude +
                     neighbor_weights[1] * point.altitude + neighbor_weights[2] * next_point.altitude,
            speed=point.speed,
            bearing=point.bearing
        ))

        prev_point = point

    return new_points
