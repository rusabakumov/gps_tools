import datetime
from datetime import datetime
import haversine
from collections import deque
from gpstools.utils import avg

EPS = 0.00005


# time - datetime object
# lat, lon, altitude - double
class TrackPoint:

    def __init__(self, time, latitude, longitude, altitude):
        self.time = time
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude

    def __repr__(self):
        return "Point %.4f, %.4f at %s" % (
            self.latitude, self.longitude, datetime.strftime(self.time, '%Y-%m-%dT%H:%M:%S.%f')
        )


class Track:

    def __init__(self, gpx_points):
        assert len(gpx_points) > 0

        self._gpx_points = gpx_points
        self._len = len(gpx_points)

        self._check_millis_format()

        self._start_time = gpx_points[0].time
        self._end_time = gpx_points[self._len - 1].time
        self._total_time = self._end_time - self._start_time

        self.lat, self.lon, self._dist = self._calculate_dist()
        self.dist_travelled = self._calculate_dist_travelled()

        self._total_distance = sum(self._dist)
        self._total_avg_speed = self._total_distance / self._total_time.total_seconds() * 3600

        self._speed = self._calculate_speed(1)
        self._max_speed = max(self._speed)
        self._avg_speed = avg(self._speed)

    # Harry's Lap Timer writes milliseconds with a leading zero, that breaks speed calculations. Checking it
    def _check_millis_format(self):
        has_millis_precision = False
        has_full_fractions = False
        for i in range(self._len):
            if self._gpx_points[i].time.microsecond > 0:
                has_millis_precision = True
            if self._gpx_points[i].time.microsecond >= 100000:
                has_full_fractions = True

        if has_millis_precision and not has_full_fractions:
            print("Looks that track has incorrect milliseconds presicion format (i.e written by Harry's Lap Timer). Fixing")
            for i in range(self._len):
                self._gpx_points[i].time = self._gpx_points[i].time.replace(
                    microsecond=self._gpx_points[i].time.microsecond * 10
                )

    def _calculate_dist(self):
        lat = []
        lon = []
        dist = []

        # zero_dist_points = 0

        prev_point = self._gpx_points[0]
        for i in range(self._len):
            cur_point = self._gpx_points[i]
            lat.append(cur_point.latitude)
            lon.append(cur_point.longitude)
            if i == 0:
                dist.append(0.0)
            else:
                cur_dist = haversine.haversine(
                    (cur_point.latitude, cur_point.longitude),
                    (prev_point.latitude, prev_point.longitude)
                )
                # if (cur_dist < EPS):
                # zero_dist_points += 1
                dist.append(cur_dist)
            prev_point = cur_point

        # print("Zero dist points: %d" % zero_dist_points)

        return lat, lon, dist

    def _calculate_speed(self, window_size):
        assert window_size >= 1
        speed_window = deque()
        speed = []

        prev_point = self._gpx_points[0]
        for i in range(self._len):
            cur_point = self._gpx_points[i]
            time_delta = cur_point.time - prev_point.time
            time_delta_micros = time_delta.seconds * 1000000 + time_delta.microseconds
            if time_delta_micros == 0:
                cur_speed = 0
            else:
                cur_speed = self._dist[i] / time_delta_micros * 1000000 * 3600

            speed_window.append(cur_speed)

            if len(speed_window) > window_size:
                speed_window.popleft()

            speed.append(avg(speed_window))
            prev_point = cur_point

        return speed

    def _calculate_dist_travelled(self):
        cur_dist = 0
        dist_travelled = []

        for i in range(self._len):
            cur_dist += self._dist[i]
            dist_travelled.append(cur_dist)

        return dist_travelled

    def print_stats(self):
        print('Start time: %s' % self._start_time)
        print('End time: %s' % self._end_time)
        print('Total time: %s' % self._total_time)
        print('Total distance travelled: %.3f km' % self._total_distance)
        print('Total average speed: %.2f kph' % self._total_avg_speed)
        print('Max speed: %.2f kph' % self._max_speed)
        print('Average speed: %.2f kph' % self._avg_speed)
        print('\n')

    def get_speed(self, speed_smoothing=3):
        return self._calculate_speed(speed_smoothing)

    def determine_activity_segments(self, allowed_pause, segment_duration_threshold):
        activity_segments = []

        segment_start_idx = None
        segment_end_idx = None
        is_segment_active = False

        def try_add_activity_segment(start_idx, end_idx):
            segment_duration = (self._gpx_points[end_idx].time - self._gpx_points[start_idx].time).total_seconds()

            if segment_duration >= segment_duration_threshold:
                new_segment = TrackActivitySegment(
                    len(activity_segments),
                    start_idx,
                    end_idx,
                    self._gpx_points[start_idx],
                    self._gpx_points[end_idx]
                )
                return [new_segment]

            return []

        for i in range(self._len):
            if segment_start_idx is None:
                # Marking current point as a candidate
                segment_start_idx = i
                segment_end_idx = None
                is_segment_active = False
            else:
                if self._dist[i] < EPS:
                    if not is_segment_active:
                        # Moving segment start forward, no movement
                        segment_start_idx = i
                        is_segment_active = False
                    else:
                        # We detected stop in current active segment, should check whether it's the end
                        if segment_end_idx is not None:
                            # We are already stopped, calculationg time passed
                            cur_pause = (self._gpx_points[i].time - self._gpx_points[
                                segment_end_idx].time).total_seconds()
                            if cur_pause > allowed_pause:
                                # If pause is above the threshold, we should end segment
                                activity_segments.extend(try_add_activity_segment(segment_start_idx, segment_end_idx))

                                segment_start_idx = None
                                segment_end_idx = None
                                is_segment_active = False

                        else:
                            # It's the first stop point, marking it as an end of segment candidate
                            segment_end_idx = i
                else:
                    # We have noticed movement in segment - it should be marked as active and end candidate should be dropped
                    is_segment_active = True
                    segment_end_idx = None

        # Adding last segment
        if segment_end_idx is None:
            segment_end_idx = self._len - 1

        activity_segments.extend(try_add_activity_segment(segment_start_idx, segment_end_idx))

        return activity_segments

    def crop_track_to_segment(self, activity_segment):
        return Track(self._gpx_points[activity_segment.start_idx:activity_segment.end_idx + 1])


class TrackActivitySegment:

    def __init__(self, idx, start_idx, end_idx, start_point, end_point):
        self._idx = idx
        self.start_idx = start_idx
        self.end_idx = end_idx

        self._start_time = start_point.time
        self._end_time = end_point.time
        self._total_time = self._end_time - self._start_time

    def print_stats(self):
        print('Activity segment #%d:' % self._idx)
        print('Start time: %s' % self._start_time)
        print('End time: %s' % self._end_time)
        print('Duration: %s' % self._total_time)
        print('\n')
