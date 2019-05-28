from gpstools.config import POINT_DISTANCE_THRESHOLD_KM
from gpstools.track.activity_detection import DEFAULT_ACTIVITY_DETECTION_PARAMS, get_activity_segments_for_track
from gpstools.track.speed_calculation import DEFAULT_SPEED_PARAMS
from gpstools.track.track import Track
from gpstools.utils import get_dist
from gpstools.viz import generate_ss_analysis_graph

POINT_ALIGNMENT_SEARCH_WINDOW = 50


class SSAnalysisTrackPoint:

    def __init__(self, idx, lat, lon, speed, dist, micros):
        self.idx = idx
        self.lat = lat
        self.lon = lon
        self.speed = speed
        self.dist = dist
        self.micros = micros


class SSAnalysisTrack:
    """Aligned representation of a track"""

    def __init__(self,
                 name,
                 points,
                 subsecond_precision,
                 is_finished,
                 max_speed,
                 avg_speed,
                 start_time,
                 end_time):
        self.len = len(points)
        self.name = name
        self.points = points
        self.subsecond_precision = subsecond_precision,
        self.is_finished = is_finished
        self.max_speed = max_speed
        self.avg_speed = avg_speed
        self.start_time = start_time
        self.end_time = end_time

    def print_stats(self):
        print('Track %s' % self.name)
        print('Start time: %s' % self.start_time)
        print('End time: %s' % self.end_time)
        print('Total time: %s' % (self.end_time - self.start_time))
        print('Total distance travelled: %.3f km' % self.points[-1].dist)
        print('Max speed: %.2f kph' % self.max_speed)
        print('Average speed: %.2f kph' % self.avg_speed)
        print('Finished: %s' % self.is_finished)
        print('\n')


class SSAnalysisGraph:

    def __init__(
            self,
            tracks,
            reference_track,
            speed_params=DEFAULT_SPEED_PARAMS,
            activity_detection_params=DEFAULT_ACTIVITY_DETECTION_PARAMS,
            point_distance_threshold_km=POINT_DISTANCE_THRESHOLD_KM):
        self.reference_track = reference_track
        self.speed_params = speed_params
        self.activity_detection_params = activity_detection_params
        self.point_distance_threshold_km = point_distance_threshold_km
        self.tracks, tracks_finished = self._select_segments_by_reference_track(tracks)

        print("Found %d tracks out of %d initial tracks" % (len(self.tracks), len(tracks)))

        self.aligned_tracks = []
        for i, original_track in enumerate(self.tracks):
            track = Track(
                original_track.name,
                original_track.points,
                speed_params=self.speed_params,
                norm_params=None
            )

            aligned_track = self._align_track_along_reference(
                self.reference_track,
                track,
                tracks_finished[i]
            )

            self.aligned_tracks.append(aligned_track)

    def print_stats(self):
        print("Comparing %d tracks" % len(self.aligned_tracks))
        for i in range(len(self.aligned_tracks)):
            print("%d:" % i)
            self.aligned_tracks[i].print_stats()

    def build_comparison_graph(self, name, title):
        generate_ss_analysis_graph(name, title, self.aligned_tracks)

    # Tries to find closest points in track along reference points
    # same_point_dist_threshold - points within this threshold counts as the same for reference points
    # dist_threshold_max - helps us understand that we moved far away from ref point
    def _align_track_along_reference(self, reference_track, track, is_finished):
        ref_points = reference_track.points
        saved_ref_idx = 0
        filtered_points = []
        missed_points_count = 0
        for i, point in enumerate(track.points):
            # Adding candidate points
            candidate_points = []
            closest_ref_point_idx = 0
            min_dist = 100000000  # Max value as a stub

            # min_ref_idx = max(saved_ref_idx - POINT_ALIGNMENT_SEARCH_WINDOW, 0)
            min_ref_idx = saved_ref_idx  # Searching points only after previous (strange behaviour in case of spins)
            max_ref_idx = min(saved_ref_idx + POINT_ALIGNMENT_SEARCH_WINDOW, len(ref_points))

            for ref_idx in range(min_ref_idx, max_ref_idx):
                dist_from_ref = get_dist(point, ref_points[ref_idx])
                candidate_points.append(ref_points[ref_idx])
                if dist_from_ref < min_dist:
                    min_dist = dist_from_ref
                    closest_ref_point_idx = ref_idx
                ref_idx += 1

            saved_ref_idx = closest_ref_point_idx

            if min_dist > self.point_distance_threshold_km:
                missed_points_count += 1

            filtered_points.append(SSAnalysisTrackPoint(
                idx=i,
                lat=point.lat,
                lon=point.lon,
                speed=track.speed[i],
                dist=reference_track.dist_from_start[closest_ref_point_idx],
                micros=track.micros_from_start[i]
            ))

        print("Done dist alignment for track %s, %d points are off the track" % (track.name, missed_points_count))

        aligned_track = SSAnalysisTrack(
            name=track.name,
            points=filtered_points,
            subsecond_precision=track.subsecond_precision,
            is_finished=is_finished,
            max_speed=track.max_speed,
            avg_speed=track.avg_speed,
            start_time=track.start_time,
            end_time=track.end_time
        )
        return aligned_track

    def _select_segments_by_reference_track(self, tracks):
        cropped_tracks = []
        tracks_finished = []

        start_point = self.reference_track.points[0]
        finish_point = self.reference_track.points[-1]

        for track in tracks:
            segment_id = 1
            for segment in get_activity_segments_for_track(track, self.activity_detection_params):
                start_coords = segment.start_point.get_coords()
                if get_dist(start_coords, start_point.get_coords()) < self.point_distance_threshold_km:
                    name_postfix = ""
                    if segment_id > 1:
                        name_postfix = "_#" + str(segment_id)

                    track_by_segment = track.crop_to_activity_segment_start(segment, track.name + name_postfix)
                    finish_index = track_by_segment.find_point_index(finish_point)

                    if finish_index is None:
                        cropped_track = track_by_segment
                        tracks_finished.append(False)
                    else:
                        cropped_track = track_by_segment.crop_to_point_idx(finish_index)
                        tracks_finished.append(True)

                    cropped_tracks.append(cropped_track)

                    segment_id += 1

        return cropped_tracks, tracks_finished
