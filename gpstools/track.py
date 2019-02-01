import datetime
from datetime import datetime
from collections import deque
from gpstools.utils import avg, get_timedelta_micros
from gpstools.gps_utils import calculate_distance, calculate_dist_travelled

EPS = 0.00005
DEFAULT_SPEED_SMOOTHING = 1


class Coordinates:

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return "Coordinate %.4f, %.4f" % (self.latitude, self.longitude)

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Coordinates):
            return self.latitude == other.latitude and self.longitude == other.longitude
        return NotImplemented

    def __hash__(self):
        return hash((self.latitude, self.longitude))


# time - datetime object
# lat, lon, altitude - double
# speed - double (m/s)
class TrackPoint:

    def __init__(self, time, latitude, longitude, altitude, speed):
        self.time = time
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.speed = speed

    def __repr__(self):
        return "Point %.4f, %.4f at %s, speed %.4f m/s" % (
            self.latitude, self.longitude, datetime.strftime(self.time, '%Y-%m-%dT%H:%M:%S.%f'), self.speed
        )

    def get_coords(self):
        return Coordinates(self.latitude, self.longitude)


class Track:

    def __init__(self, name, gpx_points):
        assert len(gpx_points) > 0

        self.name = name
        self._gpx_points = gpx_points
        self.len = len(gpx_points)
        self._speed_smoothing = DEFAULT_SPEED_SMOOTHING

        self.subsecond_precision = False
        self._check_millis_format()

        self._start_time = gpx_points[0].time
        self._end_time = gpx_points[self.len - 1].time
        self._total_time = self._end_time - self._start_time

        self.lat, self.lon, self._time, self._dist = calculate_distance(self._gpx_points)
        self.dist_travelled = calculate_dist_travelled(self._dist)

        self._total_distance = sum(self._dist)
        self._total_avg_speed = self._total_distance / self._total_time.total_seconds() * 3600

    # Harry's Lap Timer writes milliseconds with a leading zero, that breaks speed calculations. Checking it
    def _check_millis_format(self):
        has_millis_precision = False
        has_full_fractions = False
        for i in range(self.len):
            if self._gpx_points[i].time.microsecond > 0:
                has_millis_precision = True
            if self._gpx_points[i].time.microsecond >= 100000:
                has_full_fractions = True

        if has_millis_precision:
            self.subsecond_precision = True

        if has_millis_precision and not has_full_fractions:
            print("Looks that track has incorrect milliseconds presicion format (i.e written by Harry's Lap Timer). Fixing")
            for i in range(self.len):
                self._gpx_points[i].time = self._gpx_points[i].time.replace(
                    microsecond=self._gpx_points[i].time.microsecond * 10
                )

    """Use built-in gps speed data and converts it to kph units"""
    def _calculate_speed(self, window_size):
        assert window_size >= 1
        speed_window = deque()
        speed = []

        for i in range(self.len):
            cur_point = self._gpx_points[i]
            speed_window.append(cur_point.speed * 3.6)

            if len(speed_window) > window_size:
                speed_window.popleft()

            speed_window_without_zeros = list(filter(lambda x: x != 0.0, speed_window))
            if len(speed_window_without_zeros) == 0:
                speed.append(0)
            else:
                speed.append(avg(speed_window_without_zeros))

        return speed

    # Obsolete method based on inaccurate data
    # def _calculate_speed(self, window_size):
    #     assert window_size >= 1
    #     speed_window = deque()
    #     speed = []
    #
    #     prev_point = self._gpx_points[0]
    #     for i in range(self.len):
    #         cur_point = self._gpx_points[i]
    #         time_delta_micros = get_timedelta_micros(cur_point.time, prev_point.time)
    #         if time_delta_micros == 0:
    #             cur_speed = 0
    #         else:
    #             cur_speed = self._dist[i] / time_delta_micros * 1000000 * 3600
    #
    #         speed_window.append(cur_speed)
    #
    #         if len(speed_window) > window_size:
    #             speed_window.popleft()
    #
    #         speed_window_without_zeros = list(filter(lambda x: x != 0.0, speed_window))
    #         if len(speed_window_without_zeros) == 0:
    #             speed.append(0)
    #         else:
    #             speed.append(avg(speed_window_without_zeros))
    #
    #         prev_point = cur_point
    #
    #     return speed

    def print_stats(self):
        speed = self._calculate_speed(self._speed_smoothing)
        max_speed = max(speed)
        avg_speed = avg(speed)

        print('Track %s' % self.name)
        print('Start time: %s' % self._start_time)
        print('End time: %s' % self._end_time)
        print('Total time: %s' % self._total_time)
        print('Total distance travelled: %.3f km' % self._total_distance)
        print('Total average speed: %.2f kph' % self._total_avg_speed)
        print('Max speed: %.2f kph' % max_speed)
        print('Average speed: %.2f kph' % avg_speed)
        print('\n')

    def set_speed_smoothing(self, speed_smoothing):
        self._speed_smoothing = speed_smoothing

    def get_speed(self):
        return self._calculate_speed(self._speed_smoothing)

    def get_points(self):
        return self._gpx_points

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

        for i in range(self.len):
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
                            # We are already stopped, calculating time passed
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
            segment_end_idx = self.len - 1

        activity_segments.extend(try_add_activity_segment(segment_start_idx, segment_end_idx))

        return activity_segments

    def crop_track_to_segment(self, activity_segment, segment_name):
        return Track(segment_name, self._gpx_points[activity_segment.start_idx:activity_segment.end_idx + 1])


class TrackActivitySegment:

    def __init__(self, idx, start_idx, end_idx, start_point, end_point):
        self._idx = idx
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.start_point = start_point
        self.end_point = end_point

        self._start_time = start_point.time
        self._end_time = end_point.time
        self._total_time = self._end_time - self._start_time

    def print_stats(self):
        print('Activity segment #%d:' % self._idx)
        print('Start time: %s' % self._start_time)
        print('End time: %s' % self._end_time)
        print('Duration: %s' % self._total_time)
        print('\n')
