import json
import matplotlib.pyplot as plt
import os
import random
import shutil
import string
from jinja2 import Environment, PackageLoader

import gpstools

COLORS = ['red', 'blue', 'black', 'green']
COLOR_CODES = ['#4062f9', '#f44b42', '#45e069', '#fff049', '#24CBE5', '#2c6633', '#45215b', '#3c6887', '#52f2b7', '#ff3dbb', '#ff8f26']

TMP_PATH = 'tmp'
GRAPH_OUTPUT_PATH = 'viz'
GRAPH_HTML_FILE = 'graph.html'
GRAPH_JS_FILE = 'graph.js'
GRAPH_DATA_FILE = 'data.json'


def plot_distance_speed_graph(tracks):
    fig = plt.figure()
    ax = plt.Axes(fig, [0., 0., 2.5, 2.5], )
    plt.xlabel('distance (km)')
    plt.ylabel('speed (kph)')
    fig.add_axes(ax)

    for i, track in enumerate(tracks):
        color = COLORS[i]
        plt.plot(track.dist_from_start, track.speed, color=color, lw=0.75, alpha=0.8)


def plot_distance_speed_graph_aligned(tracks):
    fig = plt.figure()
    ax = plt.Axes(fig, [0., 0., 2.5, 2.5], )
    plt.xlabel('distance (km)')
    plt.ylabel('speed (kph)')
    fig.add_axes(ax)

    for i, track in enumerate(tracks):
        color = COLORS[i]
        dist_from_start = []
        speed = []
        for point in track.points:
            dist_from_start.append(point.dist)
            speed.append(point.speed)

        plt.plot(dist_from_start, speed, color=color, lw=0.75, alpha=0.8)


def generate_reference_selection_graph(tracks):
    """
    Plots distance/speed graphs of given tracks with point indices. Used for track limits selection during reference
    building. Generates separate folder with html and js to show in browser
    """

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

    with open(os.path.join(graph_path, GRAPH_DATA_FILE), "w+") as json_file:
        tracks_json = []
        for i in range(len(tracks)):
            track = tracks[i]
            data = []
            for i in range(track.len):
                data.append({
                    'idx': i,
                    'x': track.dist_from_start[i],
                    'y': track.speed[i],
                    'micros': track.micros_from_start[i]
                })

            tracks_json.append({
                "name": track.name,
                "data": data,
                "line_width": 1.0 if not track.subsecond_precision else 0.5
            })

        json.dump(
            {
                "title": "Reference selection",
                "tracks": tracks_json
            },
            json_file
        )

    return graph_path


def generate_tracks_map(tracks):
    """
    Plots distance/speed graphs of given tracks with point indices. Used for track limits selection during reference
    building. Generates separate folder with html and js to show in browser
    """

    rand_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

    graph_path = os.path.join(TMP_PATH, rand_token)
    module_path = os.path.dirname(gpstools.__file__)

    shutil.copytree(os.path.join(module_path, 'resources', 'tracks_map'),
                    graph_path)  # Fails if directory already exists
    _output_tracks_map_json(os.path.join(graph_path, GRAPH_DATA_FILE), tracks)
    return graph_path


def _output_tracks_map_json(filename, tracks):
    with open(filename, "w+") as json_file:
        tracks_json = []
        for i in range(len(tracks)):
            track = tracks[i]
            color_code = COLOR_CODES[i]
            data = []
            for i in range(track.len):
                data.append({
                    'lat': track.lat[i],
                    'lon': track.lon[i]
                })

            tracks_json.append({
                "name": track.name,
                "color": color_code,
                "data": data,
                "line_width": 1.0 if not track.subsecond_precision else 0.5
            })

        json.dump(
            {
                "tracks": tracks_json
            },
            json_file
        )


# Generates separate folder with html and js to show
def generate_ss_analysis_graph(name, graph_title, tracks):
    graph_path = os.path.join(GRAPH_OUTPUT_PATH, name)
    module_path = os.path.dirname(gpstools.__file__)
    shutil.copytree(os.path.join(module_path, 'resources', 'speed_comparison'), graph_path)  # Fails if directory already exists
    _output_ss_comparison_json(os.path.join(graph_path, GRAPH_DATA_FILE), graph_title, tracks)


def _output_ss_comparison_json(filename, title, tracks):
    with open(filename, "w+") as json_file:
        tracks_json = []
        for i in range(len(tracks)):
            track = tracks[i]
            color_code = COLOR_CODES[i]
            data = []
            for i, point in enumerate(track.points):
                data.append({
                    'x': point.dist,
                    'y': point.speed,
                    'lat': point.lat,
                    'lon': point.lon,
                    'idx': i,
                    'micros': point.micros
                })

            tracks_json.append({
                "name": track.name,
                "duration": track.points[-1].micros,
                "max_speed": track.max_speed,
                "avg_speed": track.avg_speed,
                "finished": track.is_finished,
                "color": color_code,
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
