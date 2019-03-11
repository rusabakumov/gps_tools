import React, { Component } from 'react';
import './App.css';
import { formatDuration } from './utils'

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import StatsTable from './StatsTable';
import GoogleMap from './GoogleMap'

import Highcharts from 'highcharts';

class TracksMap extends Component {
  constructor(props) {
    super(props);

    this.state = {
      tracks: [],
    };

    this.loadJson('./data.json', this.onLoadData.bind(this));
  }

  onLoadData(data) {
    // Adding string id to each track
    data.tracks.forEach(function(track, i, arr) {
      track.id = i.toString();
    });
    
    this.setState({
      tracks: data.tracks
    });
  }

  render() {
    return (
      <div className="TracksMap">
        <Container>
          <Row>
            <Col><GoogleMap tracks={this.state.tracks}/></Col>
          </Row>
        </Container>
      </div>
    )
  }

  loadJson(filename, callback) {
    console.log('Loading graph data');
    var xobj = new XMLHttpRequest();
    xobj.overrideMimeType("application/json");

    xobj.open('GET', filename, true);
    xobj.onreadystatechange = function () {
          if (xobj.readyState == 4 && xobj.status == "200") {
            // Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode
            callback(JSON.parse(xobj.responseText));
          }
    };
    xobj.send(null);
  }
}

export default TracksMap;
