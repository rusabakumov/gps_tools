import csv
import datetime
import dateutil
import gpxpy
from datetime import datetime

from gpstools.track import Track, TrackPoint

MINIMAL_TRACK_LENGTH = 100


class TrackParsingError(Exception):

    def __init__(self, message):
        self.message = message


def load_gpx_track(filename, name):
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

    if len(gpx_track) < MINIMAL_TRACK_LENGTH:
        raise TrackParsingError("Track is too short! Only %d points" % len(gpx_track))

    points = []
    for point in gpx_track:
        speed = None
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

    print('Load track %s with %d points' % (filename, len(gpx_track)))

    return Track(name, points)


RACECHRONO_TIME_FIELD = 'Time (s)'
RACECHRONO_LAT_FIELD = 'Latitude (deg)'
RACECHRONO_LON_FIELD = 'Longitude (deg)'
RACECHRONO_ALT_FIELD = 'Altitude (m)'
RACECHRONO_SPEED_FIELD = 'Speed (m/s)'

RACECHRONO_MAX_HEADER_LINES = 20
RACECHRONO_INVALID_ROWS_THRESHOLD = 50


def load_racechrono_csv_track(filename, name):
    csv_file = open(filename, newline='')

    # Seeking position for track start
    # Racechrono has several lines of headers, then empty line and the rest of the lines are actual track
    # Seeking it
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

    if len(points) < MINIMAL_TRACK_LENGTH:
        raise TrackParsingError("Track is too short! Only %d points" % len(points))

    print('Load racechrono track %s with %d points' % (filename, len(points)))

    return Track(name, points)


RACEBOX_TIME_FIELD = 'Time'
RACEBOX_LAT_FIELD = 'Lat'
RACEBOX_LON_FIELD = 'Lon'
RACEBOX_ALT_FIELD = 'Alt (m)'
RACEBOX_SPEED_FIELD = 'Speed (kph)'
RACEBOX_TIME_FORMAT = ''


def load_racebox_csv_track(filename, name):
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

    if len(points) < MINIMAL_TRACK_LENGTH:
        raise TrackParsingError("Track is too short! Only %d points" % len(points))

    print('Load racebox track %s with %d points' % (filename, len(points)))

    return Track(name, points)
