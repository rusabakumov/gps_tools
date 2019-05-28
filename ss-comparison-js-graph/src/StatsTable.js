import React, { Component } from 'react';

import Table from 'react-bootstrap/Table';
import { formatDuration } from './utils';

class StatsTable extends Component {
  constructor(props) {
    super(props);
    this.state = {
      selected_track: null
    }
  }

  render() {
    // Calculate diffs on selected
    const track_diffs = {};
    const sector_durations = {};
    const sector_diffs = {};
    
    this.props.tracks.forEach(track => {
      if (this.props.sector != null) {
        sector_durations[track.id] = this.getSectorDuration(this.props.sector, track);;
      }
    })

    if (this.state.selected_track != null) {
      // Searching for reference track
      let reference_track = null;
      this.props.tracks.forEach(track =>{
        if (track.id == this.state.selected_track) {
          reference_track = track
        }
      })

      let reference_sector_duration = null;
      if (this.props.sector != null) {
        reference_sector_duration = sector_durations[reference_track.id]
      }

      this.props.tracks.forEach(track => {
        if (track.id == reference_track.id) {
          track_diffs[track.id] = '-';
        } else if (!track.finished) {
          track_diffs[track.id] = '-'
        } else {
          track_diffs[track.id] = this.formatDurationDiff(track.duration - reference_track.duration);
        }
        if (this.props.sector != null) {
          if (sector_durations[track.id] == 0 || track.id == reference_track.id) {
            sector_diffs[track.id] = '-';
          } else {
            sector_diffs[track.id] = this.formatDurationDiff(
              sector_durations[track.id] - reference_sector_duration
            )
          }
        }
      })    
    }

    let track_index = 0;
    let rows = this.props.tracks.map(track => {
      track_index++;
      return <TrackRow 
        key={track.id} 
        idx={track_index} 
        track={track}
        track_duration_diff={track_diffs[track.id]}
        selected={this.state.selected_track == track.id}
        sector_duration={sector_durations[track.id]}
        sector_duration_diff={sector_diffs[track.id]}
        handleRowSelection={this.handleRowSelection.bind(this)}
      />
    });

    return (
      <div className="Table">
        <Table striped bordered size="sm">
          <thead>
            <tr>
              <th>#</th>
              <th>Track</th>
              <th>Time</th>
              <th>Diff</th>
              <th>Max speed</th>
              <th>Avg speed</th>
              <th>Sector time</th>
              <th>Sector diff</th>
            </tr>
          </thead>
          <tbody>
            { rows }
          </tbody>
        </Table>
      </div>
    );
  }

  getSectorDuration(sector, track) {
    let left_micros = 0;
    let left_min_dist = Number.MAX_VALUE;

    let right_micros = 0;
    let right_min_dist = Number.MAX_VALUE;
    track.data.forEach(point => {
      const dist_left = Math.abs(point.x - sector.left);
      if (dist_left < left_min_dist) {
        left_min_dist = dist_left;
        left_micros = point.micros;
      }

      const dist_right = Math.abs(point.x - sector.right);
      if (dist_right < right_min_dist) {
        right_min_dist = dist_right;
        right_micros = point.micros;
      }
    })

    return right_micros - left_micros;
  }

  formatDurationDiff(durationDiff) {
    if (durationDiff > 0) {
      return '+' + formatDuration(durationDiff);
    } else {
      return '-' + formatDuration(Math.abs(durationDiff));
    }
  }

  handleRowSelection(track_id) {
    if (this.state.selected_track == track_id) {
      this.setState({selected_track: null})
    } else {
      this.setState({selected_track: track_id})
    }
  }
}

const TrackRow = (props) => {
  let classStr = "";
  if (props.selected) {
    classStr = "table-primary"
  }
  return (
    <tr onClick={(event) => props.handleRowSelection(props.track.id)} className={classStr}>
      <th scope="row">{props.idx}</th>
      <td>{props.track.name}</td>
      <td>{formatDuration(props.track.duration)}</td>
      <td>{props.track_duration_diff}</td>
      <td>{props.track.max_speed.toFixed(2)}</td>
      <td>{props.track.avg_speed.toFixed(2)}</td>
      <td>{formatNonZeroDuration(props.sector_duration)}</td>
      <td>{props.sector_duration_diff}</td>
    </tr>
  );
}

const formatNonZeroDuration = number => {
  if (number == 0 || number == null) {
    return ""
  } else {
    return formatDuration(number)  
  }
}

export default StatsTable;
