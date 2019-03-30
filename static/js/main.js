function parse_csv(csv) {
    var series = [];
    csv.split('\n').forEach(function (line) {
        var data = line.split(',');
        if (data.length >= 2) {
            var point = [];
            data.forEach(function(val) {
                point.push(+val);
            });
            series.push(point);
        }
    });
    // TODO: sort & uniq
    return series;
}
