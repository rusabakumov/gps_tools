function formatDuration(micros) {
    var minutes = Math.floor(micros / 60000000);
    var seconds = Math.floor(micros % 60000000 / 1000000);
    var millis = Math.round(micros % 1000000 / 100000);
    return formatInt(minutes, 2) + ':' + formatInt(seconds, 2) + '.' + formatInt(millis, 1);
}

function formatInt(num, length) {
    var r = "" + num;
    while (r.length < length) {
        r = "0" + r;
    }
    return r;
}

export { formatDuration };

