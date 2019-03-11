import csv
import os
from copy import deepcopy
import datetime
from datetime import datetime
import dateutil
import gpxpy
from collections import namedtuple

from gpstools.track.track import Track, TrackPoint

CSV_EXTENSION = 'csv'
GPX_EXTENSION = 'gpx'
SUPPORTED_EXTENSIONS = [CSV_EXTENSION, GPX_EXTENSION]


class TrackParsingError(Exception):

    def __init__(self, message):
        super().__init__()
        self.message = message


TrackFile = namedtuple('TrackFile', ['path', 'name', 'ext'])


def load_track(filepath):
    track_file = _check_file_extension(filepath)
    if track_file:
        return _load_track_file(track_file)
    else:
        raise TrackParsingError("File %s is not supported!" % filepath)


def load_tracks_in_path(path):
    """ @:returns list of parsed tracks """
    track_files = []
    for f in os.listdir(path):
        track_file = _check_file_extension(os.path.join(path, f))
        if track_file:
            track_files.append(track_file)

    tracks = []
    for file in track_files:
        track_opt = _load_track_file(file)
        if track_opt:
            tracks.append(track_opt)

    print("Load %d tracks:" % len(tracks))
    for track in tracks:
        print(track.name)

    return tracks


def _check_file_extension(filepath):
    if os.path.isfile(filepath):
        path_segments = filepath.split('/')[-1].split('.')
        if len(path_segments) == 2:
            extension = path_segments[-1]
            if extension in SUPPORTED_EXTENSIONS:
                return TrackFile(filepath, path_segments[0], extension)

    return None


def _load_track_file(file):
    print('Processing file %s' % file.path)
    try:
        if file.ext == GPX_EXTENSION:
            points = _load_gpx_points(file.path)
        elif file.ext == CSV_EXTENSION:
            try:
                points = _load_racebox_csv_points(file.path)
            except TrackParsingError:
                print("Looks like not a racebox track, trying racechrono format")
                points = _load_racechrono_csv_points(file.path)
        else:
            raise TrackParsingError("File %s is not supported!" % file.path)

    except TrackParsingError as err:
        print("Skipping track %s due to: %s" % (file.path, err.message))
        return None

    fixed_points = _fix_points_errors(points)

    print('Load track %s with %d points' % (file.name, len(fixed_points)))
    return Track(file.name, fixed_points, speed_params=None, norm_params=None)


def _load_gpx_points(filename):
    gpx_file = open(filename, 'r')
    gpx = gpxpy.parse(gpx_file)

    if len(gpx.tracks) != 1:
        raise TrackParsingError("GPX track with multiple tracks!")
    if len(gpx.tracks[0].segments) != 1:
        raise TrackParsingError("GPX track with multiple segments!")

    speed_in_mps = True
    print('Parsing %s gpx track' % gpx.creator)
    if gpx.creator == 'Racebox':
        speed_in_mps = False

    gpx_track = gpx.tracks[0].segments[0].points

    points = []
    for point in gpx_track:
        if point.speed is None:
            speed = 0.0
        else:
            speed = point.speed if speed_in_mps else float(point.speed) / 3.6

        points.append(TrackPoint(
            time=point.time,
            latitude=point.latitude,
            longitude=point.longitude,
            altitude=point.elevation,
            speed=speed
        ))

    return points


RACECHRONO_TIME_FIELD = 'Time (s)'
RACECHRONO_LAT_FIELD = 'Latitude (deg)'
RACECHRONO_LON_FIELD = 'Longitude (deg)'
RACECHRONO_ALT_FIELD = 'Altitude (m)'
RACECHRONO_SPEED_FIELD = 'Speed (m/s)'

RACECHRONO_MAX_HEADER_LINES = 20
RACECHRONO_INVALID_ROWS_THRESHOLD = 50


def _load_racechrono_csv_points(filename):
    csv_file = open(filename, newline='')

    # Seeking position for track start
    # Racechrono has several lines of headers, then empty line and the rest of the lines are actual track
    # Seeking for it
    line = csv_file.readline()
    lines_skipped = 0
    if 'RaceChrono' not in line:
        raise TrackParsingError('First line should contain "RaceChrono"!')
    while line.strip() and lines_skipped < RACECHRONO_MAX_HEADER_LINES:
        line = csv_file.readline()
        lines_skipped += 1

    if lines_skipped == RACECHRONO_MAX_HEADER_LINES:
        raise TrackParsingError('Cannot parse racechrono header, check the file manually')

    print(str(csv_file.tell()))

    track = csv.DictReader(csv_file, delimiter=',')

    invalid_rows = 0
    points = []
    for row in track:
        try:
            time_seconds_float = float(row[RACECHRONO_TIME_FIELD])
            time_seconds = int(time_seconds_float)
            time_microseconds = int(time_seconds_float % 1 * 1000000)
            time = datetime.fromtimestamp(time_seconds).replace(microsecond=time_microseconds)
            points.append(TrackPoint(
                time=time,
                latitude=float(row[RACECHRONO_LAT_FIELD]),
                longitude=float(row[RACECHRONO_LON_FIELD]),
                altitude=float(row[RACECHRONO_ALT_FIELD]),
                speed=float(row[RACECHRONO_SPEED_FIELD])
            ))

        except KeyError:
            raise TrackParsingError("Found invalid row %d: %s" % (len(points) + 1, str(row)))
        except ValueError:
            invalid_rows += 1

    if invalid_rows > RACECHRONO_INVALID_ROWS_THRESHOLD:
        raise TrackParsingError("Too many invalid rows in racechrono track: %d" % invalid_rows)

    print('Load racechrono track %s with %d points' % (filename, len(points)))

    return points


RACEBOX_TIME_FIELD = 'Time'
RACEBOX_LAT_FIELD = 'Lat'
RACEBOX_LON_FIELD = 'Lon'
RACEBOX_ALT_FIELD = 'Alt (m)'
RACEBOX_SPEED_FIELD = 'Speed (kph)'
RACEBOX_TIME_FORMAT = ''


def _load_racebox_csv_points(filename):
    csv_file = open(filename, newline='')

    track = csv.DictReader(csv_file, delimiter=';')
    points = []

    for row in track:
        try:
            points.append(TrackPoint(
                time=dateutil.parser.parse(row[RACEBOX_TIME_FIELD]),
                latitude=float(row[RACEBOX_LAT_FIELD]),
                longitude=float(row[RACEBOX_LON_FIELD]),
                altitude=float(row[RACEBOX_ALT_FIELD]),
                speed=float(row[RACEBOX_SPEED_FIELD]) / 3.6  # Converting from kph to m/s
            ))

        except (KeyError, ValueError):
            raise TrackParsingError("Found invalid row %d: %s" % (len(points) + 1, str(row)))

    print('Load racebox track %s with %d points' % (filename, len(points)))

    return points


def _fix_points_errors(points):
    """Some tracks has wrong format - bundling checks together"""
    return _restore_subsecond_precision(_check_incorrect_subsecond_precision(points))


# Harry's Lap Timer writes milliseconds with a leading zero, that breaks speed calculations. Checking it
def _check_incorrect_subsecond_precision(points):
    has_millis_precision = False
    has_full_fractions = False
    for i in range(len(points)):
        if points[i].time.microsecond > 0:
            has_millis_precision = True
        if points[i].time.microsecond >= 100000:
            has_full_fractions = True

    if has_millis_precision and not has_full_fractions:
        print("Looks that track has incorrect milliseconds presicion format (i.e written by Harry's Lap Timer). Fixing")
        fixed_points = []
        for i in range(len(points)):
            fixed_point = deepcopy(points[i])
            fixed_point.time = fixed_point.time.replace(
                microsecond=fixed_point.time.microsecond * 10
            )
            fixed_points.append(fixed_point)
        return fixed_points
    else:
        return points


# Some tracks are missing milliseconds precision (like those recorded with XGPS-160 built-in logger)
def _restore_subsecond_precision(points):
    are_points_restored = False
    restored_points = []
    same_second_points = []
    current_second = points[0].time.second
    first_group = True
    for i in range(len(points)):
        point = points[i]
        if point.time.second != current_second:
            millis_fixed, fixed_points = _restore_points_within_second(same_second_points, first_group)
            restored_points.extend(fixed_points)
            first_group = False
            are_points_restored = are_points_restored | millis_fixed
            same_second_points = [point]
            current_second = point.time.second
        else:
            same_second_points.append(point)

    millis_fixed, fixed_points = _restore_points_within_second(same_second_points, first_group)
    restored_points.extend(fixed_points)
    are_points_restored = are_points_restored | millis_fixed

    if are_points_restored:
        print("Looks that track has missed subsecond precision. Fixing")

    return restored_points


def _restore_points_within_second(same_second_points, first_group):
    if len(same_second_points) > 1 and not _has_millis_precision(same_second_points):
        return True, _assign_micros_for_points(same_second_points, first_group)
    else:
        return False, same_second_points


def _has_millis_precision(points):
    has_millis_precision = False
    for i in range(len(points)):
        if points[i].time.microsecond > 0:
            has_millis_precision = True

    return has_millis_precision


def _assign_micros_for_points(points, first_group=None):
    """When group is first, it means that we have to count points as a last millis in second"""
    assert len(points) <= 10
    micros_idx = 0
    if first_group:
        micros_idx = 10 - len(points)

    restored_points = []
    for i in range(len(points)):
        point = points[i]
        restored_points.append(TrackPoint(
            time=point.time.replace(microsecond=micros_idx * 100000),
            latitude=point.latitude,
            longitude=point.longitude,
            altitude=point.altitude,
            speed=point.speed
        ))
        micros_idx += 1

    return restored_points
