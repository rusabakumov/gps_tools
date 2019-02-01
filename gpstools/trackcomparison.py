from gpstools.track import Track
from gpstools.gps_utils import get_dist
from gpstools.utils import avg

from gpstools.viz import generate_aligned_distance_speed_graph

POINT_DISTANCE_THRESHOLD_KM = 0.02
POINT_MAX_DISTANCE_THRESHOLD_KM = 0.3


class AlignedTrack(Track):

    def __init__(self, name, gpx_points, aligned_dist):
        super().__init__(name, gpx_points)
        self.aligned_dist = aligned_dist


class TrackComparison:

    def __init__(self, reference_track, tracks, point_distance_threshold_km=POINT_DISTANCE_THRESHOLD_KM):
        self._reference_track = reference_track
        self._tracks = self._crop_tracks_to_finish(reference_track, tracks)

        self._aligned_tracks = []
        for track in tracks:
            aligned_track = AlignedTrack(
                track.name,
                track.get_points(),
                self.align_distances_along_track(
                    self._reference_track,
                    track,
                    point_distance_threshold_km,
                    POINT_MAX_DISTANCE_THRESHOLD_KM
                )
            )
            aligned_track.set_speed_smoothing(track._speed_smoothing)

            self._aligned_tracks.append(aligned_track)


    # self._aligned_tracks = []
        # for track in tracks:
        #     self._aligned_tracks.append(self.align_track_along_reference(
        #         self._reference_track,
        #         track,
        #         POINT_DISTANCE_THRESHOLD_KM,
        #         POINT_MAX_DISTANCE_THRESHOLD_KM
        #     ))

    # Tries to find closest points in track along reference points
    # same_point_dist_threshold - points within this threshold counts as the same for reference points
    # dist_threshold_max - helps us understand that we moved far away from ref point
    def align_distances_along_track(self, reference_track, track, same_point_dist_threshold, dist_threshold_max):
        ref_points = reference_track.reference_points
        aligned_dist = []

        no_candidates_points = 0
        dist_duplicatation_points = 0

        saved_ref_idx = 0

        points = track.get_points()
        for i in range(track.len):
            point = points[i]

            # Searching for suitable ref points for point
            ref_idx = saved_ref_idx
            dist_from_ref = get_dist(point, ref_points[ref_idx])
            while same_point_dist_threshold < dist_from_ref < dist_threshold_max and ref_idx < reference_track.len - 1:
                ref_idx += 1
                dist_from_ref = get_dist(point, ref_points[ref_idx])

            # Adding candidate points
            candidate_points = []
            closest_ref_point_idx = 0
            min_dist = dist_threshold_max + 1000  # Max value as a stub

            while dist_from_ref <= same_point_dist_threshold and ref_idx < reference_track.len - 1:
                candidate_points.append(ref_points[ref_idx])
                if dist_from_ref < min_dist:
                    min_dist = dist_from_ref
                    closest_ref_point_idx = ref_idx
                ref_idx += 1
                dist_from_ref = get_dist(point, ref_points[ref_idx])

            # Selecting best point for track
            # ref_point_candidates.append(len(candidate_points))
            if len(candidate_points) == 0:
                no_candidates_points += 1
                print("Point with id %d has no distance found" % i)
                aligned_dist.append(reference_track.dist_travelled[saved_ref_idx])
            else:
                if closest_ref_point_idx == saved_ref_idx:
                    dist_duplicatation_points += 1
                aligned_dist.append(reference_track.dist_travelled[closest_ref_point_idx])
                saved_ref_idx = closest_ref_point_idx  # We will start next iteration from this index

        print("Done dist alignment for track %s" % track.name)
        print("Found %d no candidates points" % no_candidates_points)
        print("Found %d dist duplication points" % dist_duplicatation_points)

        return aligned_dist

    def _crop_tracks_to_finish(self, reference_track, tracks):
        last_point = reference_track.reference_points[self._reference_track.len-1]

        cropped_tracks = []
        for track in tracks:
            points = track.get_points()
            finish_idx = track.len - 1
            while get_dist(last_point, points[finish_idx]) > POINT_DISTANCE_THRESHOLD_KM and finish_idx > 0:
                finish_idx -= 1

            if finish_idx == 0:
                print("Failed to find finish point for track %s" % track.name)
                finish_idx = track.len - 1 # We assume that track finished earlier

            cropped_track = Track(track.name, points[0:finish_idx])
            cropped_track.set_speed_smoothing(track._speed_smoothing)

            cropped_tracks.append(cropped_track)

        return cropped_tracks


    # Tries to find closest points in track along reference points
    # same_point_dist_threshold - points within this threshold counts as the same for reference points
    # dist_threshold_max - helps us understand that we moved far away from ref point
    def align_track_along_reference(self, reference_track, track, same_point_dist_threshold, dist_threshold_max):
        points = track.get_points()
        saved_idx = 0  # Used to store offset for the next point

        aligned_points = []  # Here we will store points for reference

        ref_point_candidates = []  # Array for stats - number of candidates for each point
        missed_points = 0  # Points without candidates - shows that we have an error in alignment

        for ref_point in reference_track.reference_points:
            # Searching for suitable points for reference track

            idx = saved_idx
            dist_from_ref = get_dist(ref_point, points[idx])
            while same_point_dist_threshold < dist_from_ref < dist_threshold_max and idx < track.len - 1:
                idx += 1
                dist_from_ref = get_dist(ref_point, points[idx])

            # Adding candidate points
            candidate_points = []
            closest_point_idx = 0
            min_dist = dist_threshold_max + 1000  # Max value as a stub

            while dist_from_ref <= same_point_dist_threshold and idx < track.len - 1:
                candidate_points.append(points[idx])
                if dist_from_ref < min_dist:
                    min_dist = dist_from_ref
                    closest_point_idx = idx
                idx += 1
                dist_from_ref = get_dist(ref_point, points[idx])

            # Selecting best point for track
            ref_point_candidates.append(len(candidate_points))
            if len(candidate_points) == 0:
                missed_points += 1
                aligned_points.append(points[saved_idx])  # Adding last point, it won't affect stats
            else:
                aligned_points.append(points[closest_point_idx])
                saved_idx = closest_point_idx  # We will start next iteration from this index

        print("Done alignment for track %s" % track.name)
        print("Average number of candidate points: %.1f" % avg(ref_point_candidates))
        print("Found %d reference points with no candidates" % missed_points)

        print("Original stats:")
        track.print_stats()

        aligned_track = Track(track.name, aligned_points)
        aligned_track.set_speed_smoothing(track._speed_smoothing)

        print("Aligned stats:")
        aligned_track.print_stats()

        return aligned_track

    def print_stats(self):
        print("Comparison of %d tracks" % len(self._tracks))

    def build_comparison_graph(self, name, title):
        generate_aligned_distance_speed_graph(name, title, self._aligned_tracks)
