from collections import namedtuple
from collections import deque
from gpstools.utils import avg, get_timedelta_micros, get_dist

TrackSpeedParams = namedtuple('TrackSpeedParams', ['use_provided_speed', 'smoothing_1hz', 'smoothing_10hz'])

DEFAULT_SPEED_PARAMS = TrackSpeedParams(use_provided_speed=True, smoothing_1hz=1, smoothing_10hz=3)


def calculate_speed_with_provided_data(points, window_size):
    """Uses built-in gps speed data and converts it to kph units"""
    assert window_size >= 1
    speed_window = deque()
    speed = []

    for i in range(len(points)):
        cur_point = points[i]
        speed_window.append(cur_point.speed * 3.6)

        if len(speed_window) > window_size:
            speed_window.popleft()

        speed_window_without_zeros = list(filter(lambda x: x != 0.0, speed_window))
        if len(speed_window_without_zeros) == 0:
            speed.append(0)
        else:
            speed.append(avg(speed_window_without_zeros))

    return speed


# Method based on inaccurate data, used when no speed data available in track
def calculate_speed_by_distance(points, window_size):
    assert window_size >= 1
    speed_window = deque()
    speed = []

    prev_point = points[0]
    for i in range(len(points)):
        cur_point = points[i]
        time_delta_micros = get_timedelta_micros(cur_point.time, prev_point.time)
        if time_delta_micros == 0:
            cur_speed = 0
        else:
            cur_speed = get_dist(cur_point, prev_point) / time_delta_micros * 1000000 * 3600

        speed_window.append(cur_speed)

        if len(speed_window) > window_size:
            speed_window.popleft()

        speed_window_without_zeros = list(filter(lambda x: x != 0.0, speed_window))
        if len(speed_window_without_zeros) == 0:
            speed.append(0)
        else:
            speed.append(avg(speed_window_without_zeros))

        prev_point = cur_point

    return speed
