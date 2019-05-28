from collections import namedtuple
from collections import deque
import math
from gpstools.utils import get_bearing_diff, sign

TrackProfileParams = namedtuple('TrackProfileParams', ['straight_degrees_bounds', 'window_size_min_points'])

DEFAULT_TRACK_PROFILE_PARAMS = TrackProfileParams(
    straight_degrees_bounds=1.5,
    window_size_min_points=5
)


TYPE_STRAIGHT = "straight"
TYPE_TURN = "turn"


class TrackProfileSegment:

    def __init__(self, start_idx, end_idx):
        self.type = ""
        self.start_idx = start_idx
        self.end_idx = end_idx


class StraightProfileSegment(TrackProfileSegment):

    def __init__(self, start_idx, end_idx, bearing):
        super().__init__(start_idx, end_idx)
        self.type = TYPE_STRAIGHT
        self.bearing = bearing


class TurnProfileSegment(TrackProfileSegment):

    def __init__(self, start_idx, end_idx, rotation):
        super().__init__(start_idx, end_idx)
        self.type = TYPE_TURN
        self.rotation = rotation


class TrackProfile:

    def __init__(self):
        self.segments = []


def build_track_profile(track, params):
    point_window = deque()
    last_segment = None
    segments = []

    def update_point_window(idx, point):
        point_window.append((idx, point))
        if len(point_window) > params.window_size_min_points:
            point_window.popleft()

    def get_segment_suggestion():
        min_bearing, max_bearing, total_bearing = 500, -500, 0
        for idx, p in point_window:
            total_bearing += p.bearing
            if p.bearing < min_bearing:
                min_bearing = p.bearing
            if p.bearing > max_bearing:
                max_bearing = p.bearing

        avg_bearing = total_bearing / len(point_window)
        if math.fabs(get_bearing_diff(avg_bearing, min_bearing)) < params.straight_degrees_bounds and \
                math.fabs(get_bearing_diff(avg_bearing, max_bearing)) < params.straight_degrees_bounds:
            return StraightProfileSegment(point_window[0][0], None, avg_bearing)
        else:
            return TurnProfileSegment(
                point_window[0][0],
                None,
                sign(get_bearing_diff(point_window[0][1].bearing, point_window[-1][1].bearing))
            )

    if not track.has_bearing_data:
        print('Cannot build profile for track with no bearing data!')
        return None



    for i, point in enumerate(track.points):
        update_point_window(i, point)
        suggestion = get_segment_suggestion()
        if last_segment is None:
            last_segment = suggestion
        elif last_segment.type != suggestion.type:
