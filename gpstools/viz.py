import matplotlib.pyplot as plt

COLORS = ['red', 'blue', 'black']
smoothing = [1, 10]


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
        plt.plot(track.dist_travelled, track.get_speed(smoothing[i]), color=color, lw=0.75, alpha=0.8)


def plot_2d_track(track):
    fig = plt.figure(facecolor='0.25')
    ax = plt.Axes(fig, [0., 0., 2., 2.], )
    ax.set_aspect('equal')
    ax.set_axis_off()
    fig.add_axes(ax)
    plt.plot(track.lon, track.lat, color='deepskyblue', lw=0.3, alpha=0.8)
