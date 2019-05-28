import haversine

from gpstools.config import SPARSE_TRACK_DISTANCE_THRESHOLD_KM
from gpstools.track.track import Track


def build_sparse_track(track, distance_threshold=SPARSE_TRACK_DISTANCE_THRESHOLD_KM):
    last_point = track.points[0]
    reference_points = [last_point]

    for point in track.points:
        dist = haversine.haversine(
            (point.lat, point.lon),
            (last_point.lat, last_point.lon)
        )

        if dist > distance_threshold:
            reference_points.append(point)
            last_point = point

    return Track(
        name=track.name,
        points=reference_points,
        speed_params=track.speed_params,
        norm_params=track.norm_params
    )
