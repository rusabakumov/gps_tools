import haversine


def build_sparse_track(track, distance_threshold):
    original_points = track.get_points()
    last_point = original_points[0]
    reference_points = [last_point]

    for point in track.get_points():
        dist = haversine.haversine(
            (point.latitude, point.longitude),
            (last_point.latitude, last_point.longitude)
        )

        if dist > distance_threshold:
            reference_points.append(point)
            last_point = point

    return reference_points
