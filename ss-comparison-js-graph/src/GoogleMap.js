import React from 'react'
import scriptLoader from 'react-async-script-loader'

class GoogleMap extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			"map": null
		}
	}

	componentWillReceiveProps ({ isScriptLoaded, isScriptLoadSucceed }) {
		if (isScriptLoaded && !this.props.isScriptLoaded ) {
			if (isScriptLoadSucceed) {
				this.initMap();
			} else {
            	alert("Cannot load google maps js")
			}
		}
	}

	render() {
		this.renderMap();
		return (    
			<div id='map' style={{height: "600px"}}></div>
		)
	}

	initMap() {
		var map = new window.google.maps.Map(document.getElementById('map'), {
		  zoom: 3,
		  center: {lat: 0, lng: -180},
		  mapTypeId: 'satellite'
		});

		this.setState({"map": map});
	}

	renderMap() {
		if (this.state.map) {
			var bounds = this.determineMapBounds();
			this.state.map.fitBounds(bounds);
			this.props.tracks.forEach(track => {
				var coords = [];
				track.data.forEach(point => {
					coords.push({
						lat: point.lat,
						lng: point.lon
					});
				});

				var polyline = new window.google.maps.Polyline({
				  path: coords,
				  geodesic: true,
				  strokeColor: track.color,
				  strokeOpacity: 1.0,
				  strokeWeight: 2
				});

				polyline.setMap(this.state.map);
			});
		}
	}

	determineMapBounds() {
		var initialPoint = {lat: 0, lng: -180};
		if (this.props.tracks.length > 0) {
			if (this.props.tracks[0].data.length > 0) {
				initialPoint = {lat: this.props.tracks[0].data[0].lat, lng: this.props.tracks[0].data[0].lon};
			}
		}

		var bounds = new window.google.maps.LatLngBounds(initialPoint, initialPoint);
		this.props.tracks.forEach(track => {
			track.data.forEach(point => {
				bounds.extend({lat: point.lat, lng: point.lon});	
			})
		});

		return bounds;
	}
}

export default scriptLoader(
  'https://maps.googleapis.com/maps/api/js?key=<insert your key>'
)(GoogleMap)
