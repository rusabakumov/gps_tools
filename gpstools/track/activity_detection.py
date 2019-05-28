from collections import namedtuple
from gpstools.track.track import TrackActivitySegment

ActivityDetectionParams = namedtuple('ActivityDetectionParams',
                                     ['distance_eps', 'segment_max_allow_pause', 'segment_min_duration'])

DEFAULT_ACTIVITY_DETECTION_PARAMS = ActivityDetectionParams(
    distance_eps=0.00005,
    segment_max_allow_pause=5,
    segment_min_duration=100
)


def get_activity_segments_for_track(track, activity_detection_params=DEFAULT_ACTIVITY_DETECTION_PARAMS):
    activity_segments = []

    segment_start_idx = None
    segment_end_idx = None
    is_segment_active = False

    def try_add_activity_segment(start_idx, end_idx):
        segment_duration = (track.points[end_idx].time - track.points[start_idx].time).total_seconds()

        if segment_duration >= activity_detection_params.segment_min_duration:
            new_segment = TrackActivitySegment(
                len(activity_segments),
                start_idx,
                end_idx,
                track.points[start_idx],
                track.points[end_idx]
            )
            return [new_segment]
        else:
            return []

    for i in range(track.len):
        if segment_start_idx is None:
            # Marking current point as a candidate
            segment_start_idx = i
            segment_end_idx = None
            is_segment_active = False
        else:
            if track.dist[i] < activity_detection_params.distance_eps:
                if not is_segment_active:
                    # Moving segment start forward, no movement
                    segment_start_idx = i
                    is_segment_active = False
                else:
                    # We detected stop in current active segment, should check whether it's the end
                    if segment_end_idx is not None:
                        # We are already stopped, calculating time passed
                        cur_pause = (track.points[i].time - track.points[segment_end_idx].time).total_seconds()
                        if cur_pause > activity_detection_params.segment_max_allow_pause:
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

    if segment_start_idx is not None:
        # Adding last segment
        if segment_end_idx is None:
            segment_end_idx = track.len - 1

        activity_segments.extend(try_add_activity_segment(segment_start_idx, segment_end_idx))

    return activity_segments
