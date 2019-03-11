import haversine


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


# Calculates haversine dist between two TrackPoint or Coordinates objects
def get_dist(point1, point2):
    return haversine.haversine(
        (point1.latitude, point1.longitude),
        (point2.latitude, point2.longitude)
    )


def print_tracks_stats(tracks):
    print("Total %d tracks" % len(tracks))
    for i in range(len(tracks)):
        print("%d:" % i)
        tracks[i].print_stats()

