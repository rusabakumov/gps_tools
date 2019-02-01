import haversine


# Calculates haversine dist between two TrackPoint or Coordinates objects
def get_dist(point1, point2):
    return haversine.haversine(
        (point1.latitude, point1.longitude),
        (point2.latitude, point2.longitude)
    )


# Returns three arrays - latitudes, longitudes and distance from previous point
def calculate_distance(points):
    assert len(points) > 0

    lat = []
    lon = []
    time = []
    dist = []

    prev_point = points[0]
    for i in range(len(points)):
        cur_point = points[i]
        lat.append(cur_point.latitude)
        lon.append(cur_point.longitude)
        time.append(cur_point.time)
        if i == 0:
            dist.append(0.0)
        else:
            cur_dist = get_dist(cur_point, prev_point)
            dist.append(cur_dist)
        prev_point = cur_point

    return lat, lon, time, dist


def calculate_dist_travelled(dist):
    cur_dist = 0
    dist_travelled = []

    for i in range(len(dist)):
        cur_dist += dist[i]
        dist_travelled.append(cur_dist)

    return dist_travelled
