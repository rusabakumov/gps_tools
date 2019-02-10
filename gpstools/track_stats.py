#!/usr/local/bin/python3

import sys
import os
import getopt
from collections import namedtuple
from gpstools.parser import *
from gpstools.gps_utils import get_dist
from gpstools.config import START_RADIUS_KM


CSV_EXTENSION = 'csv'
GPX_EXTENSION = 'gpx'
SUPPORTED_EXTENSIONS = [CSV_EXTENSION, GPX_EXTENSION]
ACTIVITY_DISTANCE_THRESHOLD_KM = 2.0

TrackFile = namedtuple('TrackFile', ['path', 'name', 'ext'])


def load_tracks(path):
    """ @:returns list of parsed tracks """
    track_files = []
    for f in os.listdir(path):
        filepath = os.path.join(path, f)
        if os.path.isfile(filepath):
            path_segments = filepath.split('/')[-1].split('.')
            if len(path_segments) == 2:
                extension = path_segments[-1]
                if extension in SUPPORTED_EXTENSIONS:
                    track_files.append(TrackFile(filepath, path_segments[0], extension))

    tracks = []
    for file in track_files:
        print('Processing file %s' % file.path)
        try:
            if file.ext == GPX_EXTENSION:
                tracks.append(load_gpx_track(file.path, file.name))
            elif file.ext == CSV_EXTENSION:
                try:
                    tracks.append(load_racebox_csv_track(file.path, file.name))
                except TrackParsingError:
                    print("Looks like not a racebox track, trying racechrono format")
                    tracks.append(load_racechrono_csv_track(file.path, file.name))
            else:
                print("Unknown extension for file %s" % file.path)
        except TrackParsingError as err:
            print("Skipping track %s due to: %s" % (file.path, err.message))

    print("Load %d tracks:" % len(tracks))
    for track in tracks:
        print(track.name)

    return tracks


def find_common_activity_segments(tracks):
    tracks_with_activity = []
    for track in tracks:
        tracks_with_activity.append(TrackWithActivitySegments(track, track.get_activity_segments()))

    activity_start_points = {}
    for track in tracks_with_activity:
        for segment in track.segments:
            start_coords = segment.start_point.get_coords()
            if start_coords not in activity_start_points:
                activity_start_points[start_coords] = 0

            # Comparing with other coords
            for key in activity_start_points:
                if get_dist(start_coords, key) < START_RADIUS_KM:
                    activity_start_points[key] += 1

    most_popular_coord = None
    max_value = 0
    for key in activity_start_points:
        if activity_start_points[key] > max_value:
            most_popular_coord = key
            max_value = activity_start_points[key]

    assert most_popular_coord

    print("Found suitable start location at %s with %d segments" % (str(most_popular_coord), max_value))

    return select_activity_segments_by_start_point(most_popular_coord, tracks_with_activity)


def select_activity_segments_by_start_point(reference_coords, tracks):
    cropped_tracks = []
    for track in tracks:
        segment_id = 1
        for segment in track.get_activity_segments():
            start_coords = segment.start_point.get_coords()
            if get_dist(start_coords, reference_coords) < START_RADIUS_KM:
                cropped_tracks.append(
                    track.crop_to_activity_segment(segment, track.name + "_" + str(segment_id))
                )
                segment_id += 1

    return cropped_tracks


def select_segments_by_reference_track(reference_track, tracks, allowed_pause, segment_duration_threshold):
    cropped_tracks = []
    tracks_finished = []
    for track in tracks:
        segment_id = 1
        for segment in track.get_activity_segments(allowed_pause, segment_duration_threshold):
            start_coords = segment.start_point.get_coords()
            if get_dist(start_coords, reference_track.start_point.get_coords()) < START_RADIUS_KM:
                name_postfix = ""
                if segment_id > 1:
                    name_postfix = "_#" + str(segment_id)

                track_by_segment = track.crop_to_activity_segment_start(segment, track.name + name_postfix)
                finish_index = track_by_segment.find_point_index(reference_track.finish_point)

                cropped_track = None
                if finish_index is None:
                    cropped_track = track_by_segment
                    tracks_finished.append(False)
                else:
                    cropped_track = track_by_segment.crop_to_point_idx(finish_index)
                    tracks_finished.append(True)

                cropped_tracks.append(cropped_track)

                segment_id += 1

    return cropped_tracks, tracks_finished


def filter_tracks_by_reference(reference_track, tracks):
    filtered_tracks = []
    for track in tracks:
        if track.contains_point(reference_track.start_point):
            filtered_tracks.append(track)

    return filtered_tracks


def print_tracks_stats(tracks):
    print("Total %d tracks" % len(tracks))
    for i in range(len(tracks)):
        print("%d:" % i)
        tracks[i].print_stats()


def parse_args(argv):
    try:
        opts, args = getopt.getopt(argv, "hp:", ["path="])
    except getopt.GetoptError:
        print('track_stats.py -p <path>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('track_stats.py -p <path>')
            sys.exit()
        elif opt in ("-p", "--path"):
            return arg


if __name__ == "__main__":
    path = parse_args(sys.argv[1:])
    print("Processing path %s" % path)
    tracks = load_tracks(path)

    # Prompt to continue

    #cropped_tracks = find_common_activity_segments(tracks)

    # Prompt to select reference

    #print_tracks_stats(cropped_tracks)

    # Prompt to select finish point

