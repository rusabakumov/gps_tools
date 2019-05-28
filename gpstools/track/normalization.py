from collections import namedtuple
from gpstools.track import track

TrackNormalizationParams = namedtuple('TrackNormalizationParams', ['neighbor_weights'])

DEFAULT_TRACK_NORMALIZATION_PARAMS = TrackNormalizationParams(neighbor_weights=None)


def normalize_by_neighbor_weights(points, neighbor_weights):
    new_points = []

    prev_point = points[0]
    for i, point in enumerate(points):
        next_point = points[i + 1] if i < len(points) - 1 else points[i]

        new_points.append(track.TrackPoint(
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
