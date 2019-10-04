# gps_tools

Tools for analyzing racing gps tracks (in .gpx, .kml, .csv formats)and building comprasion graphs. Tested only for rally special stages (one-way race with different start and finish points)

Not supposed to work out of the box, still require tuning for each case.

[gpstools](https://github.com/rusabakumov/gps_tools/tree/master/gpstools) contains python library for parsing tracks, splitting into segments and building some simple stats

[ss-comparison-js-graph](https://github.com/rusabakumov/gps_tools/tree/master/ss-comparison-js-graph) contains single-page react app template for visualizing tracks preprocessed by gpstools