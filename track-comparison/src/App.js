import React, { Component } from 'react';
import './App.css';
import { formatDuration } from './utils'

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import StatsTable from './StatsTable';
import GoogleMap from './GoogleMap'

import Highcharts from 'highcharts';

class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      tracks: [],
      sector: null
    };

    this.loadJson('./data.json', this.onLoadData.bind(this));
  }

  onLoadData(data) {
    // Adding string id to each track
    data.tracks.forEach(function(track, i, arr) {
      track.id = i.toString();
    });

    document.title = data.title

    const chart = this.buildGraph(data.tracks, data.title);

    this.setState({
      title: data.title,
      tracks: data.tracks,
      chart: chart
    });
  }

  render() {
    return (
      <div className="App">
        <Container>
          <Row>
            <Col id="graph"/>
          </Row>
          <Row>
            <Col><StatsTable tracks={this.state.tracks} sector={this.state.sector}/></Col>
          </Row>
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

  buildGraph(series, title) {
    var names = [];

    // Adding series params and constructing name
    series.forEach(function(track, i, arr) {
        names.push(track.name)
        track.lineWidth = track.line_width;
        track.turboThreshold = 0;
    });

    return Highcharts.chart('graph', {

        chart: {
            zoomType: 'x',
            events: {
                selection: this.selectionHandler.bind(this)
            }
        },

        title: {
            text: title
        },

        subtitle: {
            text: names.join(' vs ')
        },

        tooltip: {
            useHTML: true,
            formatter: this.tooltipFormatter,
            valueDecimals: 2,
            valueSuffix: ' kph',
            shared: true,
            crosshairs: true
        },

        xAxis: {
            title: {
                text: 'Distance from start (km)'
            },
            type: 'linear',
        },

        yAxis: {
            title: {
                text: 'Speed (kph)'
            }
        },

        series: series,

        plotOptions: {
            line: {
                allowPointSelect: true,
                tooltip: {
                }
            }
        },

        credits: {
            enabled: false
        },

        exporting: {
            enabled: false
        }
    });
  }

  tooltipFormatter() {
      var first = this.points[0];
      var str = '<b>dist:</b> ' + first.x.toFixed(2) + 'km</br><b>time:</b> ' + formatDuration(first.point.micros);

      this.points.forEach(function (point) {
          var value = '<b>' + point.series.name + '</b>: ' + point.point.y.toFixed(2) + 'kph ' + formatDuration(point.point.micros);
          str = str + '</br>' + value;
      })

      return str
  }

  selectionHandler(event) {
      event.preventDefault();
      let xAxis = this.state.chart.xAxis[0];
      // var text;
      // if (event.xAxis) {
      //     text = 'min: ' + Highcharts.numberFormat(event.xAxis[0].min, 2) + ', max: ' + Highcharts.numberFormat(event.xAxis[0].max, 2);
      // } else {
      //     text = 'Selection reset';
      // }
      // console.log(text);

      // Drawing selection
      xAxis.removePlotBand('mask');
      xAxis.addPlotBand({
          id: 'mask',
          from: event.xAxis[0].min,
          to: event.xAxis[0].max,
          color: 'rgba(170, 203, 255, 0.4)',
          events: {
            'click': this.removeSector.bind(this)
          }
      });

      // Updating sector data
      this.setState({
        sector: {
          left: event.xAxis[0].min,
          right: event.xAxis[0].max,
        }
      });
  }

  removeSector(event) {
    this.state.chart.xAxis[0].removePlotBand('mask');
    this.setState({
      sector: null
    });
  }
}

export default App;
