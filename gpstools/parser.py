import gpxpy
import datetime
from datetime import datetime
import csv

from gpstools.gpstrack import Track, TrackPoint


# Returns list of TrackPoint objects
def load_gpx_track(filename):
    gpx_file = open(filename, 'r')
    gpx = gpxpy.parse(gpx_file)

    assert len(gpx.tracks) == 1
    assert len(gpx.tracks[0].segments) == 1
    assert len(gpx.tracks[0].segments[0].points) > 100
    gpx_track = gpx.tracks[0].segments[0].points

    points = []
    for point in gpx_track:
        points.append(TrackPoint(
            time=point.time,
            latitude=point.latitude,
            longitude=point.longitude,
            altitude=point.elevation
        ))

    print('Load track %s with %d points' % (filename, len(gpx_track)))

    return Track(points)


TIME_FIELD = 'Time (s)'
LAT_FIELD = 'Latitude (deg)'
LON_FIELD = 'Longitude (deg)'
ALT_FIELD = 'Altitude (m)'


def load_racechrono_csv_track(filename):
    csv_file = open(filename, newline='')

    track = csv.DictReader(csv_file, delimiter=',')

    points = []
    for row in track:
        time_seconds = int(float(row[TIME_FIELD]))
        time = datetime.fromtimestamp(time_seconds)
        points.append(TrackPoint(
            time=time,
            latitude=float(row[LAT_FIELD]),
            longitude=float(row[LON_FIELD]),
            altitude=float(row[ALT_FIELD])
        ))

    assert len(points) >= 1
    print('Load racechrono track %s with %d points' % (filename, len(points)))

    return Track(points)