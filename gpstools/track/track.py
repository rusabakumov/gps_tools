import datetime
from datetime import datetime

from gpstools.config import POINT_DISTANCE_THRESHOLD_KM
from gpstools.track.speed_calculation import *


class Coords:

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def __repr__(self):
        return "Coordinate %.4f, %.4f" % (self.lat, self.lon)

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Coords):
            return self.lat == other.lat and self.lon == other.lon
        return NotImplemented

    def __hash__(self):
        return hash((self.lat, self.lon))


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
        if self.speed:
            return "Point %.4f, %.4f at %s, speed %.4f m/s" % (
                self.latitude, self.longitude, datetime.strftime(self.time, '%Y-%m-%dT%H:%M:%S.%f'), self.speed
            )
        else:
            return "Point %.4f, %.4f at %s" % (
                self.latitude, self.longitude, datetime.strftime(self.time, '%Y-%m-%dT%H:%M:%S.%f')
            )

    def get_coords(self):
        return Coords(self.latitude, self.longitude)


class Track:

    def __init__(self, name, points, speed_params, norm_params):
        self.name = name
        self.points = points
        self.speed_params = speed_params if speed_params else DEFAULT_SPEED_PARAMS
        self.norm_params = norm_params if norm_params else None  # Not used now

        self.len = len(points)
        assert len(points) > 0

        # Initializes len, lat, dist, dist_from_start, micros_from_start and other arrays
        self._init_point_stat_arrays()

        self.subsecond_precision = self._has_subsecond_precision()
        self.speed = self._calculate_speed()

        self._init_stats()

    def _has_speed_data(self):
        """
        Some tracks do not have exact speed data present in track,
        so we need to fall back to inaccurate speed calculation methods
        """
        speed_data_available = True
        for point in self.points:
            if point.speed is None:
                print('Point without speed %s!' % str(point))
                speed_data_available = False

        return speed_data_available

    def _has_subsecond_precision(self):
        for i in range(self.len):
            if self.points[i].time.microsecond > 0:
                return True

    def _init_point_stat_arrays(self):
        self.lat = []
        self.lon = []
        self.time = []
        self.dist = []
        self.dist_from_start = []
        self.micros_from_start = []

        prev_point = self.points[0]
        start_time = self.points[0].time
        dist_from_start = 0.0

        for i in range(self.len):
            cur_point = self.points[i]
            self.lat.append(cur_point.latitude)
            self.lon.append(cur_point.longitude)
            self.time.append(cur_point.time)
            self.micros_from_start.append(get_timedelta_micros(cur_point.time, start_time))

            if i == 0:
                point_dist = 0.0
            else:
                point_dist = get_dist(cur_point, prev_point)

            dist_from_start += point_dist
            self.dist_from_start.append(dist_from_start)
            self.dist.append(point_dist)

            prev_point = cur_point

    def _calculate_speed(self):
        """Returns array of speed in kph for each point in given track"""
        if self.subsecond_precision:
            smoothing_window = self.speed_params.smoothing_10hz
        else:
            smoothing_window = self.speed_params.smoothing_1hz

        if self.speed_params.use_provided_speed and self._has_speed_data():
            print('Using built-in speed')
            return calculate_speed_with_provided_data(self.points, smoothing_window)
        else:
            print('Calculating speed based on distance')
            return calculate_speed_by_distance(self.points, smoothing_window)

    def _init_stats(self):
        self._start_time = self.points[0].time
        self._end_time = self.points[self.len - 1].time
        self._total_time = self._end_time - self._start_time

        self._total_distance = self.dist_from_start[-1]
        self._total_avg_speed = self._total_distance / self._total_time.total_seconds() * 3600

        self.max_speed = max(self.speed)
        self.avg_speed = avg(self.speed)

    def print_stats(self):
        print('Track %s' % self.name)
        print('Start time: %s' % self._start_time)
        print('End time: %s' % self._end_time)
        print('Total time: %s' % self._total_time)
        print('Total distance travelled: %.3f km' % self._total_distance)
        print('Total average speed: %.2f kph' % self._total_avg_speed)
        print('Max speed: %.2f kph' % self.max_speed)
        print('Average speed: %.2f kph' % self.avg_speed)
        print('\n')

    def find_point_index(self, point_to_check):
        for i in range(self.len):
            if get_dist(point_to_check, self.points[i]) < POINT_DISTANCE_THRESHOLD_KM:
                return i

        return None

    def crop_to_point_idx(self, index):
        if index < 0 or index >= self.len:
            print("Invalid point index for cropping!")
            return self
        else:
            return Track(
                self.name,
                self.points[:index],
                self.speed_params,
                self.norm_params
            )

    def crop_from_point_idx(self, index):
        if index < 0 or index >= self.len:
            print("Invalid point index for cropping!")
            return self
        else:
            return Track(
                self.name,
                self.points[index:],
                self.speed_params,
                self.norm_params
            )

    def crop_to_activity_segment(self, activity_segment, segment_name):
        return Track(
            segment_name,
            self.points[activity_segment.start_idx:activity_segment.end_idx + 1],
            self.speed_params,
            self.norm_params
        )

    def crop_to_activity_segment_start(self, activity_segment, segment_name):
        """Here we use only start point of activity segment. There can be several stops on road"""
        return Track(
            segment_name,
            self.points[activity_segment.start_idx:],
            self.speed_params,
            self.norm_params
        )


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
