from gpstools.gps_utils import calculate_distance, calculate_dist_travelled
from gpstools.track_utils import build_sparse_track
from gpstools.utils import get_numeric_array_stats_without_zeros, calculate_time_diffs

POINT_DISTANCE_THRESHOLD_KM = 0.005


# Reference track is a special track with a sparse points.
# It's used to align another tracks along it and count stats for comparison
class ReferenceTrack:

    def __init__(self, track):
        self.reference_points = build_sparse_track(track, POINT_DISTANCE_THRESHOLD_KM)
        self.len = len(self.reference_points)
        self.lat, self.lon, self._time, self._dist = calculate_distance(self.reference_points)
        self.dist_travelled = calculate_dist_travelled(self._dist)

        self._start_time = self.reference_points[0].time
        self._end_time = self.reference_points[self.len - 1].time
        self._total_time = self._end_time - self._start_time

    def print_stats(self):
        print("Reference track stats:")
        print("Total %d points" % len(self.reference_points))
        print("Distance between points (km):")
        print(get_numeric_array_stats_without_zeros(self._dist))
        print("Time difference between points (ms):")
        print(get_numeric_array_stats_without_zeros(calculate_time_diffs(self._time)))
        print('Total distance travelled: %.3f km' % sum(self._dist))

