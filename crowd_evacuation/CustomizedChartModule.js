// customized script to draw graph of amount of saved and killed agents over time

var ChartModule = function(series, canvas_width, canvas_height) {
    // Create the tag:
    Chart.defaults.global.defaultFontColor='black';
    var canvas_tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
    canvas_tag += "style='border:1px solid; margin-top:30px; margin-bottom:50px'></canvas>";
    // Append it to #elements
    var canvas = $(canvas_tag)[0];
    $("#elements").append(canvas);
    // Create the context and the drawing controller:
    var context = canvas.getContext("2d");

    var convertColorOpacity = function(hex) {

        if (hex.indexOf('#') != 0) {
            return 'rgba(0,0,0,0.1)';
        }

        hex = hex.replace('#', '');
        r = parseInt(hex.substring(0, 2), 16);
        g = parseInt(hex.substring(2, 4), 16);
        b = parseInt(hex.substring(4, 6), 16);
        return 'rgba(' + r + ',' + g + ',' + b + ',0.1)';
    };

    // Prep the chart properties and series:
    var datasets = []
    for (var i in series) {
        var s = series[i];
        var new_series = {
            label: s.Label,
            borderColor: s.Color,
            backgroundColor: convertColorOpacity(s.Color),
            data: []
        };
        datasets.push(new_series);
    }

    var chartData = {
        labels: [],
        datasets: datasets
    };

    var chartOptions = {
        responsive: true,
        title: {
            display: true,
            text: 'Number of agents saved and killed over time',
            fontFamily: 'Helvetica',
            fontSize: '14'
        },
        tooltips: {
            mode: 'index',
            intersect: false
        },
        hover: {
            mode: 'nearest',
            intersect: true
        },
        scales: {
            xAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'time step'

                },
                ticks: {
                    maxTicksLimit: 11
                }
            }],
            yAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Number of agents'
                },
                ticks: {
                    min: 0
                }
            }]
        }
    };

    var chart = new Chart(context, {
        type: 'line',
        data: chartData,
        options: chartOptions
    });

    this.render = function(data) {
        chart.data.labels.push(control.tick);
        for (i = 0; i < data.length; i++) {
            chart.data.datasets[i].data.push(data[i]);
        }
        chart.update();
    };

    this.reset = function() {
        while (chart.data.labels.length) { chart.data.labels.pop(); }
        chart.data.datasets.forEach(function(dataset) {
            while (dataset.data.length) { dataset.data.pop(); }
        });
        chart.update();
    };
};
