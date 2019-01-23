import matplotlib.pyplot as plt
import json
import os
from jinja2 import Environment, PackageLoader

COLORS = ['red', 'blue', 'black']

GRAPH_OUTPUT_PATH = 'viz'
GRAPH_HTML_FILE = 'graph.html'
GRAPH_JS_FILE = 'graph.js'
GRAPH_DATA_FILE = 'data.json'


def plot_distance_speed_graph(tracks):
    fig = plt.figure()
    ax = plt.Axes(fig, [0., 0., 2.5, 2.5], )
    plt.xlabel('distance (km)')
    plt.ylabel('speed (kph)')
    plt.title('SU2 cooler777')
    fig.add_axes(ax)

    for i in range(len(tracks)):
        track = tracks[i]
        color = COLORS[i]
        plt.plot(track.dist_travelled, track.get_speed(), color=color, lw=0.75, alpha=0.8)


# Generates separate folder with html and js to show
def generate_distance_speed_graph(name, graph_title, tracks):
    graph_path = os.path.join(GRAPH_OUTPUT_PATH, name)
    os.makedirs(graph_path)

    env = Environment(loader=PackageLoader('gpstools', 'templates'))
    html_template = env.get_template(GRAPH_HTML_FILE + '.j2')
    js_template = env.get_template(GRAPH_JS_FILE + '.j2')

    with open(os.path.join(graph_path, GRAPH_HTML_FILE), 'w') as html_file:
        html_template.stream().dump(html_file)

    with open(os.path.join(graph_path, GRAPH_JS_FILE), 'w') as js_file:
        js_template.stream(graph_title=graph_title).dump(js_file)

    _output_distance_speed_json(os.path.join(graph_path, GRAPH_DATA_FILE), tracks)


def _output_distance_speed_json(filename, tracks):
    with open(filename, "w+") as json_file:
        tracks_json = []
        for track in tracks:
            data = []
            speed_data = track.get_speed()
            for i in range(track.len):
                data.append((track.dist_travelled[i], speed_data[i]))

            tracks_json.append({
                "name": track.name,
                "data": data
            })

        json.dump(tracks_json, json_file)


def plot_2d_track(track):
    fig = plt.figure(facecolor='0.25')
    ax = plt.Axes(fig, [0., 0., 2., 2.], )
    ax.set_aspect('equal')
    ax.set_axis_off()
    fig.add_axes(ax)
    plt.plot(track.lon, track.lat, color='deepskyblue', lw=0.3, alpha=0.8)
