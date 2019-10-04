(window.webpackJsonp=window.webpackJsonp||[]).push([[0],{18:function(t,e,a){},22:function(t,e,a){t.exports=a(37)},28:function(t,e,a){},37:function(t,e,a){"use strict";a.r(e);var n=a(0),i=a.n(n),o=a(19),r=a.n(o),s=(a(28),a(1)),l=a(2),c=a(4),d=a(3),u=a(5),p=a(6);a(18);function h(t){var e=Math.floor(t/6e7),a=Math.floor(t%6e7/1e6),n=Math.round(t%1e6/1e5);return m(e,2)+":"+m(a,2)+"."+m(n,1)}function m(t,e){for(var a=""+t;a.length<e;)a="0"+a;return a}var f=a(15),k=a.n(f),v=a(7),g=a.n(v),b=a(8),E=a.n(b),w=a(20),y=a.n(w),x=function(t){function e(t){var a;return Object(s.a)(this,e),(a=Object(c.a)(this,Object(d.a)(e).call(this,t))).state={selected_track:null},a}return Object(u.a)(e,t),Object(l.a)(e,[{key:"render",value:function(){var t=this,e={},a={},n={};if(this.props.tracks.forEach(function(e){null!=t.props.sector&&(a[e.id]=t.getSectorDuration(t.props.sector,e))}),null!=this.state.selected_track){var o=null;this.props.tracks.forEach(function(e){e.id==t.state.selected_track&&(o=e)});var r=null;null!=this.props.sector&&(r=a[o.id]),this.props.tracks.forEach(function(i){i.id==o.id?e[i.id]="-":i.finished?e[i.id]=t.formatDurationDiff(i.duration-o.duration):e[i.id]="-",null!=t.props.sector&&(0==a[i.id]||i.id==o.id?n[i.id]="-":n[i.id]=t.formatDurationDiff(a[i.id]-r))})}var s=0,l=this.props.tracks.map(function(o){return s++,i.a.createElement(_,{key:o.id,idx:s,track:o,track_duration_diff:e[o.id],selected:t.state.selected_track==o.id,sector_duration:a[o.id],sector_duration_diff:n[o.id],handleRowSelection:t.handleRowSelection.bind(t)})});return i.a.createElement("div",{className:"Table"},i.a.createElement(y.a,{striped:!0,bordered:!0,size:"sm"},i.a.createElement("thead",null,i.a.createElement("tr",null,i.a.createElement("th",null,"#"),i.a.createElement("th",null,"Track"),i.a.createElement("th",null,"Time"),i.a.createElement("th",null,"Diff"),i.a.createElement("th",null,"Max speed"),i.a.createElement("th",null,"Avg speed"),i.a.createElement("th",null,"Sector time"),i.a.createElement("th",null,"Sector diff"))),i.a.createElement("tbody",null,l)))}},{key:"getSectorDuration",value:function(t,e){var a=0,n=Number.MAX_VALUE,i=0,o=Number.MAX_VALUE;return e.data.forEach(function(e){var r=Math.abs(e.x-t.left);r<n&&(n=r,a=e.micros);var s=Math.abs(e.x-t.right);s<o&&(o=s,i=e.micros)}),i-a}},{key:"formatDurationDiff",value:function(t){return t>0?"+"+h(t):"-"+h(Math.abs(t))}},{key:"handleRowSelection",value:function(t){this.state.selected_track==t?this.setState({selected_track:null}):this.setState({selected_track:t})}}]),e}(n.Component),_=function(t){var e="";return t.selected&&(e="table-primary"),i.a.createElement("tr",{onClick:function(e){return t.handleRowSelection(t.track.id)},className:e},i.a.createElement("th",{scope:"row"},t.idx),i.a.createElement("td",null,t.track.name),i.a.createElement("td",null,h(t.track.duration)),i.a.createElement("td",null,t.track_duration_diff),i.a.createElement("td",null,t.track.max_speed.toFixed(2)),i.a.createElement("td",null,t.track.avg_speed.toFixed(2)),i.a.createElement("td",null,S(t.sector_duration)),i.a.createElement("td",null,t.sector_duration_diff))},S=function(t){return 0==t||null==t?"":h(t)},j=x,M=a(21),O=a.n(M),D=function(t){function e(t){var a;return Object(s.a)(this,e),(a=Object(c.a)(this,Object(d.a)(e).call(this,t))).state={map:null,polyline:null,markers:[],infowindows:[]},a}return Object(u.a)(e,t),Object(l.a)(e,[{key:"componentWillReceiveProps",value:function(t){var e=t.isScriptLoaded,a=t.isScriptLoadSucceed;e&&!this.props.isScriptLoaded&&(a?this.initMap():alert("Cannot load google maps js"))}},{key:"render",value:function(){return this.renderMap(),i.a.createElement("div",{id:"map",style:{height:"600px"}})}},{key:"initMap",value:function(){var t=new window.google.maps.Map(document.getElementById("map"),{zoom:3,center:{lat:0,lng:-180},mapTypeId:"satellite"});this.setState({map:t})}},{key:"renderMap",value:function(){if(this.state.map){var t=this.determineMapBounds();this.state.map.fitBounds(t),this.renderTrack(),this.renderSpeedPoints()}}},{key:"determineMapBounds",value:function(){var t={lat:0,lng:-180};this.props.map_points.length>0&&(t={lat:this.props.map_points[0].lat,lng:this.props.map_points[0].lon});var e=new window.google.maps.LatLngBounds(t,t);return this.props.map_points.forEach(function(t){e.extend({lat:t.lat,lng:t.lon})}),e}},{key:"renderTrack",value:function(){if(this.state.map){var t=this.determineMapBounds();this.state.map.fitBounds(t);var e=[];this.props.map_points.forEach(function(t){e.push({lat:t.lat,lng:t.lon})}),this.state.polyline?this.state.polyline.setPath(e):(this.state.polyline=new window.google.maps.Polyline({path:e,geodesic:!0,strokeColor:"#3393FF",strokeOpacity:1,strokeWeight:2}),this.state.polyline.setMap(this.state.map))}}},{key:"renderSpeedPoints",value:function(){var t=this;this.state.map&&(this.state.markers.forEach(function(t){t.setVisible(!1)}),this.state.markers.length=0,this.state.infowindows.forEach(function(t){t.close()}),this.state.infowindows.length=0,this.props.speed_points.forEach(function(e){var a,n=new window.google.maps.Marker({position:{lat:e.lat,lng:e.lon},icon:{url:"marker6.png"},draggable:!1,map:t.state.map}),i="<table>";for(a=0;a<t.props.tracks.length;a++)i+="<tr><td>",i+=t.props.tracks[a].name+":</td><td>"+e.speeds[a].toFixed(1)+"km/h",i+="</td></tr>";i+="</table>";var o=new window.google.maps.InfoWindow({content:i});n.addListener("mouseover",t.showInfoWindow.bind(t,o,n)),n.addListener("mouseout",t.hideInfoWindow.bind(t,o)),t.state.markers.push(n),t.state.infowindows.push(o)}))}},{key:"showInfoWindow",value:function(t,e){t.open(this.state.map,e)}},{key:"hideInfoWindow",value:function(t){t.close()}}]),e}(i.a.Component),L=O()("https://maps.googleapis.com/maps/api/js?key=AIzaSyDIL_0ywQ2g6ShN_GgxhNjfllBSPXGzFFo")(D),A=a(16),B=a.n(A),T=function(t){function e(t){var a;return Object(s.a)(this,e),(a=Object(c.a)(this,Object(d.a)(e).call(this,t))).state={tracks:[],map_points:[],speed_points:[],sector:null},a.loadJson("./data.json",a.onLoadData.bind(Object(p.a)(Object(p.a)(a)))),a}return Object(u.a)(e,t),Object(l.a)(e,[{key:"onLoadData",value:function(t){t.tracks.forEach(function(t,e,a){t.id=e.toString()}),document.title=t.title;var e=this.buildGraph(t.tracks,t.title);this.setState({title:t.title,tracks:t.tracks,map_points:t.map_points,speed_points:t.speed_points,chart:e})}},{key:"render",value:function(){return i.a.createElement("div",{className:"SSComparison"},i.a.createElement(k.a,null,i.a.createElement(g.a,null,i.a.createElement(E.a,{id:"graph"})),i.a.createElement(g.a,null,i.a.createElement(E.a,null,i.a.createElement(j,{tracks:this.state.tracks,sector:this.state.sector}))),i.a.createElement(g.a,null,i.a.createElement(E.a,null,i.a.createElement(L,{tracks:this.state.tracks,map_points:this.state.map_points,speed_points:this.state.speed_points})))))}},{key:"loadJson",value:function(t,e){console.log("Loading graph data");var a=new XMLHttpRequest;a.overrideMimeType("application/json"),a.open("GET",t,!0),a.onreadystatechange=function(){4==a.readyState&&"200"==a.status&&e(JSON.parse(a.responseText))},a.send(null)}},{key:"buildGraph",value:function(t,e){var a=[];return t.forEach(function(t,e,n){a.push(t.name),t.lineWidth=t.line_width,t.turboThreshold=0}),B.a.chart("graph",{chart:{zoomType:"x",events:{selection:this.selectionHandler.bind(this)}},title:{text:e},subtitle:{text:a.join(" vs ")},tooltip:{useHTML:!0,formatter:this.tooltipFormatter,valueDecimals:2,valueSuffix:" kph",shared:!0,crosshairs:!0},xAxis:{title:{text:"Distance from start (km)"},type:"linear"},yAxis:{title:{text:"Speed (kph)"}},series:t,plotOptions:{line:{allowPointSelect:!0,tooltip:{}}},credits:{enabled:!1},exporting:{enabled:!1}})}},{key:"tooltipFormatter",value:function(){var t=this.points[0],e="<b>dist:</b> "+t.x.toFixed(2)+"km</br><b>time:</b> "+h(t.point.micros);return this.points.forEach(function(t){var a="<b>"+t.series.name+"</b>: "+t.point.y.toFixed(2)+"kph "+h(t.point.micros);e=e+"</br>"+a}),e}},{key:"selectionHandler",value:function(t){t.preventDefault();var e=this.state.chart.xAxis[0];e.removePlotBand("mask"),e.addPlotBand({id:"mask",from:t.xAxis[0].min,to:t.xAxis[0].max,color:"rgba(170, 203, 255, 0.4)",events:{click:this.removeSector.bind(this)}}),this.setState({sector:{left:t.xAxis[0].min,right:t.xAxis[0].max}})}},{key:"removeSector",value:function(t){this.state.chart.xAxis[0].removePlotBand("mask"),this.setState({sector:null})}}]),e}(n.Component);n.Component,Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));r.a.render(i.a.createElement(T,null),document.getElementById("root")),"serviceWorker"in navigator&&navigator.serviceWorker.ready.then(function(t){t.unregister()})}},[[22,2,1]]]);
//# sourceMappingURL=main.954f56d0.chunk.js.map