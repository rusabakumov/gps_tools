import React from 'react'
import scriptLoader from 'react-async-script-loader'

class GoogleMap extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			"map": null,
			"polyline": null,
			"markers": [],
			"infowindows": []
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

			this.renderTrack();
			this.renderSpeedPoints();
		}
	}

	determineMapBounds() {
		var initialPoint = {lat: 0, lng: -180};

		if (this.props.map_points.length > 0) {
			initialPoint = {lat: this.props.map_points[0].lat, lng: this.props.map_points[0].lon};
		}

		var bounds = new window.google.maps.LatLngBounds(initialPoint, initialPoint);
		this.props.map_points.forEach(point => {
			bounds.extend({lat: point.lat, lng: point.lon});
		});

		return bounds;
	}

	renderTrack() {
	    if (this.state.map) {
	        var bounds = this.determineMapBounds();
            this.state.map.fitBounds(bounds);

	        var coords = [];
            this.props.map_points.forEach(point => {
                coords.push({
                    lat: point.lat,
                    lng: point.lon
                });
            });

	        if (!this.state.polyline) {
                this.state.polyline = new window.google.maps.Polyline({
                    path: coords,
                    geodesic: true,
                    strokeColor: '#3393FF',
                    strokeOpacity: 1.0,
                    strokeWeight: 2
                });
                this.state.polyline.setMap(this.state.map);
	        } else {
	            this.state.polyline.setPath(coords);
	        }
		}
	}

	renderSpeedPoints() {
	    if (this.state.map) {
            // Clearing old markers and infowindows, if any
            this.state.markers.forEach(marker => {
                marker.setVisible(false);
            });
            this.state.markers.length = 0

            this.state.infowindows.forEach(infowindow => {
                infowindow.close();
            });
            this.state.infowindows.length = 0

	        this.props.speed_points.forEach(point => {
                var marker = new window.google.maps.Marker({
                    position: {
                        lat: point.lat,
                        lng: point.lon
                    },
                    icon: {
                        url: "marker6.png"
                    },
//                    icon: {
//                      path: window.google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
//                      strokeColor: '#34eb89',
//                      strokeWeight: 2,
//                      scale: 2
//
//                    },
                    draggable: false,
                    map: this.state.map
                });

                var speed_stats = "<table>";
                var i;
                for (i = 0; i < this.props.tracks.length; i++) {
                    speed_stats += "<tr><td>";
                    speed_stats += this.props.tracks[i].name + ':</td><td>' + point.speeds[i].toFixed(1) + 'km/h';
                    speed_stats += "</td></tr>";
                }
                speed_stats += "</table>"

                var infowindow = new window.google.maps.InfoWindow({
                  content: speed_stats
                });

                marker.addListener('mouseover', this.showInfoWindow.bind(this, infowindow, marker));
                marker.addListener('mouseout', this.hideInfoWindow.bind(this, infowindow));

                this.state.markers.push(marker);
                this.state.infowindows.push(infowindow);
            });
		}
	}

	showInfoWindow(infowindow, marker) {
	    infowindow.open(this.state.map, marker);
    }

    hideInfoWindow(infowindow) {
        infowindow.close();
    }
}

//  https://developers-dot-devsite-v2-prod.appspot.com/maps/documentation/javascript/reference/marker?hl=ru#Marker.mouseover


//			var infowindow = new google.maps.InfoWindow({
//              content: contentString
//            });

export default scriptLoader(
  'https://maps.googleapis.com/maps/api/js?key=<key here>'
)(GoogleMap)
