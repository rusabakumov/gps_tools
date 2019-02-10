(window.webpackJsonp=window.webpackJsonp||[]).push([[0],{20:function(t,e,a){t.exports=a(31)},26:function(t,e,a){},28:function(t,e,a){},31:function(t,e,a){"use strict";a.r(e);var n=a(0),r=a.n(n),i=a(17),o=a.n(i),l=(a(26),a(8)),c=a(9),s=a(11),u=a(10),d=a(12),h=a(4);a(28);function m(t){var e=Math.floor(t/6e7),a=Math.floor(t%6e7/1e6),n=Math.round(t%1e6/1e5);return f(e,2)+":"+f(a,2)+"."+f(n,1)}function f(t,e){for(var a=""+t;a.length<e;)a="0"+a;return a}var p=a(19),k=a.n(p),v=a(14),b=a.n(v),E=a(15),x=a.n(E),y=a(18),_=a.n(y),S=function(t){function e(t){var a;return Object(l.a)(this,e),(a=Object(s.a)(this,Object(u.a)(e).call(this,t))).state={selected_track:null},a}return Object(d.a)(e,t),Object(c.a)(e,[{key:"render",value:function(){var t=this,e={},a={},n={};if(this.props.tracks.forEach(function(e){null!=t.props.sector&&(a[e.id]=t.getSectorDuration(t.props.sector,e))}),null!=this.state.selected_track){var i=null;this.props.tracks.forEach(function(e){e.id==t.state.selected_track&&(i=e)});var o=null;null!=this.props.sector&&(o=a[i.id]),this.props.tracks.forEach(function(r){r.id==i.id?e[r.id]="-":r.finished?e[r.id]=t.formatDurationDiff(r.duration-i.duration):e[r.id]="-",null!=t.props.sector&&(0==a[r.id]||r.id==i.id?n[r.id]="-":n[r.id]=t.formatDurationDiff(a[r.id]-o))})}var l=0,c=this.props.tracks.map(function(i){return l++,r.a.createElement(g,{key:i.id,idx:l,track:i,track_duration_diff:e[i.id],selected:t.state.selected_track==i.id,sector_duration:a[i.id],sector_duration_diff:n[i.id],handleRowSelection:t.handleRowSelection.bind(t)})});return r.a.createElement("div",{className:"Table"},r.a.createElement(_.a,{striped:!0,bordered:!0,size:"sm"},r.a.createElement("thead",null,r.a.createElement("tr",null,r.a.createElement("th",null,"#"),r.a.createElement("th",null,"Track"),r.a.createElement("th",null,"Time"),r.a.createElement("th",null,"Diff"),r.a.createElement("th",null,"Max speed"),r.a.createElement("th",null,"Avg speed"),r.a.createElement("th",null,"Sector time"),r.a.createElement("th",null,"Sector diff"))),r.a.createElement("tbody",null,c)))}},{key:"getSectorDuration",value:function(t,e){var a=0,n=Number.MAX_VALUE,r=0,i=Number.MAX_VALUE;return e.data.forEach(function(e){var o=Math.abs(e.x-t.left);o<n&&(n=o,a=e.micros);var l=Math.abs(e.x-t.right);l<i&&(i=l,r=e.micros)}),r-a}},{key:"formatDurationDiff",value:function(t){return t>0?"+"+m(t):"-"+m(Math.abs(t))}},{key:"handleRowSelection",value:function(t){this.state.selected_track==t?this.setState({selected_track:null}):this.setState({selected_track:t})}}]),e}(n.Component),g=function(t){var e="";return t.selected&&(e="table-primary"),r.a.createElement("tr",{onClick:function(e){return t.handleRowSelection(t.track.id)},className:e},r.a.createElement("th",{scope:"row"},t.idx),r.a.createElement("td",null,t.track.name),r.a.createElement("td",null,m(t.track.duration)),r.a.createElement("td",null,t.track_duration_diff),r.a.createElement("td",null,t.track.max_speed.toFixed(2)),r.a.createElement("td",null,t.track.avg_speed.toFixed(2)),r.a.createElement("td",null,w(t.sector_duration)),r.a.createElement("td",null,t.sector_duration_diff))},w=function(t){return 0==t||null==t?"":m(t)},j=S,A=a(13),O=a.n(A),D=function(t){function e(t){var a;return Object(l.a)(this,e),(a=Object(s.a)(this,Object(u.a)(e).call(this,t))).state={tracks:[],sector:null},a.loadJson("./data.json",a.onLoadData.bind(Object(h.a)(Object(h.a)(a)))),a}return Object(d.a)(e,t),Object(c.a)(e,[{key:"onLoadData",value:function(t){t.tracks.forEach(function(t,e,a){t.id=e.toString()}),document.title=t.title;var e=this.buildGraph(t.tracks,t.title);this.setState({title:t.title,tracks:t.tracks,chart:e})}},{key:"render",value:function(){return r.a.createElement("div",{className:"App"},r.a.createElement(k.a,null,r.a.createElement(b.a,null,r.a.createElement(x.a,{id:"graph"})),r.a.createElement(b.a,null,r.a.createElement(x.a,null,r.a.createElement(j,{tracks:this.state.tracks,sector:this.state.sector})))))}},{key:"loadJson",value:function(t,e){console.log("Loading graph data");var a=new XMLHttpRequest;a.overrideMimeType("application/json"),a.open("GET",t,!0),a.onreadystatechange=function(){4==a.readyState&&"200"==a.status&&e(JSON.parse(a.responseText))},a.send(null)}},{key:"buildGraph",value:function(t,e){var a=[];return t.forEach(function(t,e,n){a.push(t.name),t.lineWidth=t.line_width,t.turboThreshold=0}),O.a.setOptions({colors:["#002eff","#f44b42","#3ee866","#ddcf30","#24CBE5","#2c6633","#45215b","#FFF263","#6AF9C4"]}),O.a.chart("graph",{chart:{zoomType:"x",events:{selection:this.selectionHandler.bind(this)}},title:{text:e},subtitle:{text:a.join(" vs ")},tooltip:{useHTML:!0,formatter:this.tooltipFormatter,valueDecimals:2,valueSuffix:" kph",shared:!0,crosshairs:!0},xAxis:{title:{text:"Distance from start (km)"},type:"linear"},yAxis:{title:{text:"Speed (kph)"}},series:t,plotOptions:{line:{allowPointSelect:!0,tooltip:{}}},credits:{enabled:!1},exporting:{enabled:!1}})}},{key:"tooltipFormatter",value:function(){var t=this.points[0],e="<b>dist:</b> "+t.x.toFixed(2)+"km</br><b>time:</b> "+m(t.point.micros);return this.points.forEach(function(t){var a="<b>"+t.series.name+"</b>: "+t.point.y.toFixed(2)+"kph "+m(t.point.micros);e=e+"</br>"+a}),e}},{key:"selectionHandler",value:function(t){t.preventDefault();var e=this.state.chart.xAxis[0];e.removePlotBand("mask"),e.addPlotBand({id:"mask",from:t.xAxis[0].min,to:t.xAxis[0].max,color:"rgba(170, 203, 255, 0.4)",events:{click:this.removeSector.bind(this)}}),this.setState({sector:{left:t.xAxis[0].min,right:t.xAxis[0].max}})}},{key:"removeSector",value:function(t){this.state.chart.xAxis[0].removePlotBand("mask"),this.setState({sector:null})}}]),e}(n.Component);Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));o.a.render(r.a.createElement(D,null),document.getElementById("root")),"serviceWorker"in navigator&&navigator.serviceWorker.ready.then(function(t){t.unregister()})}},[[20,2,1]]]);
//# sourceMappingURL=main.e34f01fe.chunk.js.map