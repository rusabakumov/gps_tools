import haversine

from gpstools.config import POINT_DISTANCE_THRESHOLD_KM
from gpstools.track.track import Track


def build_sparse_track(track, distance_threshold=POINT_DISTANCE_THRESHOLD_KM):
    last_point = track.points[0]
    reference_points = [last_point]

    for point in track.points:
        dist = haversine.haversine(
            (point.latitude, point.longitude),
            (last_point.latitude, last_point.longitude)
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
