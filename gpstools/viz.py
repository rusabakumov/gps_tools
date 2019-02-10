import matplotlib.pyplot as plt
import json
import os
from jinja2 import Environment, PackageLoader
from gmplot import gmplot
import random
import string
import shutil
import gpstools

COLORS = ['red', 'blue', 'black', 'green']

TMP_PATH = 'tmp'
GRAPH_OUTPUT_PATH = 'viz'
GRAPH_HTML_FILE = 'graph.html'
GRAPH_JS_FILE = 'graph.js'
GRAPH_DATA_FILE = 'data.json'


def plot_distance_speed_graph(distances, speeds):
    assert len(distances) == len(speeds)

    fig = plt.figure()
    ax = plt.Axes(fig, [0., 0., 2.5, 2.5], )
    plt.xlabel('distance (km)')
    plt.ylabel('speed (kph)')
    fig.add_axes(ax)

    for i in range(len(distances)):
        color = COLORS[i]
        plt.plot(distances[i], speeds[i], color=color, lw=0.75, alpha=0.8)


def plot_distance_speed_graph_for_tracks(tracks):
    fig = plt.figure()
    ax = plt.Axes(fig, [0., 0., 2.5, 2.5], )
    plt.xlabel('distance (km)')
    plt.ylabel('speed (kph)')
    fig.add_axes(ax)

    for i in range(len(tracks)):
        track = tracks[i]
        color = COLORS[i]
        plt.plot(track.get_dist(), track.get_speed(), color=color, lw=0.75, alpha=0.8)


# Uses dist_travelled from aligned
def plot_aligned_distance_speed_graph(reference_track, aligned_tracks, unaligned_tracks):
    fig = plt.figure()
    ax = plt.Axes(fig, [0., 0., 2.5, 2.5], )
    plt.xlabel('distance (km)')
    plt.ylabel('speed (kph)')
    fig.add_axes(ax)

    unaligned = len(unaligned_tracks)

    for i in range(unaligned):
        track = unaligned_tracks[i]
        color = COLORS[i]
        plt.plot(track.dist_travelled, track.get_speed(), color=color, lw=0.75, alpha=0.8)

    for i in range(len(aligned_tracks)):
        track = aligned_tracks[i]
        color = COLORS[i + unaligned]
        plt.plot(reference_track.dist_travelled, track.get_speed(), color=color, lw=0.75, alpha=0.8)


# Generates separate folder with html and js to show
def generate_distance_speed_graph(name, graph_title, tracks):
    graph_path = os.path.join(GRAPH_OUTPUT_PATH, name)
    module_path = os.path.dirname(gpstools.__file__)
    shutil.copytree(os.path.join(module_path, 'resources', 'speed_comparison'), graph_path)  # Fails if directory already exists
    _output_distance_speed_json(os.path.join(graph_path, GRAPH_DATA_FILE), graph_title, tracks)


# Generates separate folder with html and js to show
def generate_reference_selection_graph(tracks):
    rand_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

    graph_path = os.path.join(TMP_PATH, rand_token)
    os.makedirs(graph_path, exist_ok=True)

    env = Environment(loader=PackageLoader('gpstools', 'resources/reference_selection'))
    html_template = env.get_template(GRAPH_HTML_FILE + '.j2')
    js_template = env.get_template(GRAPH_JS_FILE + '.j2')

    with open(os.path.join(graph_path, GRAPH_HTML_FILE), 'w') as html_file:
        html_template.stream().dump(html_file)

    with open(os.path.join(graph_path, GRAPH_JS_FILE), 'w') as js_file:
        js_template.stream().dump(js_file)

    _output_distance_speed_json(os.path.join(graph_path, GRAPH_DATA_FILE), "reference selection", tracks)

    return graph_path


def _output_distance_speed_json(filename, title, tracks):
    with open(filename, "w+") as json_file:
        tracks_json = []
        for track in tracks:
            data = []
            dist_data = track.get_dist()
            speed_data = track.get_speed()
            for i in range(track.len):
                data.append({
                    'x': dist_data[i],
                    'y': speed_data[i],
                    'idx': i,
                    'micros': track.micros[i]
                })

            tracks_json.append({
                "name": track.name,
                "duration": track.micros[-1],
                "max_speed": track.max_speed,
                "avg_speed": track.avg_speed,
                "finished": track.finished,
                "data": data,
                "line_width": 1.0 if not track.subsecond_precision else 0.5
            })

        json.dump(
            {
                "title": title,
                "tracks": tracks_json
            },
            json_file
        )


def plot_2d_track(track):
    fig = plt.figure(facecolor='0.25')
    ax = plt.Axes(fig, [0., 0., 2., 2.], )
    ax.set_aspect('equal')
    ax.set_axis_off()
    fig.add_axes(ax)
    plt.plot(track.lon, track.lat, color='deepskyblue', lw=0.3, alpha=0.8)


def plot_google_maps_track(track, filename):
    min_lat, max_lat, min_lon, max_lon = \
        min(track.lat), max(track.lat), \
        min(track.lon), max(track.lon)

    # Create empty map with zoom level 16
    mymap = gmplot.GoogleMapPlotter(
        min_lat + (max_lat - min_lat) / 2,
        min_lon + (max_lon - min_lon) / 2,
        16)

    mymap.plot(track.lat, track.lon, 'blue', edge_width=1)

    mymap.draw(filename)
