$(function() {

    var cpu_info_updater = new CpuInfoUpdater({
        label_load: '#load',
        chart_container: '#cpu-load-chart',
        interval: 100
    });
    cpu_info_updater.start_updating();

});


function CpuInfoUpdater(params) {

    var self = this;

    this.__label_load = $(params.label_load);

    this.__chart_container = $(params.chart_container);

    this.__chart_series = [{
        data: [],
        lines: {
            fill: true
        },
        shadowSize: 0
    }];

    this.__chart_plot = null;

    this.actual_load = null;

    this.interval = params.interval;

    this.start_updating = function() {
        self.__get_chart_data(function() {
            self.__init_chart();
            self.__draw_chart();
        });
        setTimeout(
            function() { setInterval(self.__update, self.interval); },
            self.interval
        );
    }

    this.__update = function() {
        $.get(
            '/api/computer_info/processor.load',
            function(data) {
                var cpu_load = data['processor.load'];
                if(self.actual_load !== cpu_load) {
                    self.actual_load = cpu_load;
                    self.__label_load.text(cpu_load);
                }
                if(self.__chart_series[0].data.length >= 100) {
                    self.__chart_series[0].data.shift();
                }
                var now = new Date();
                now = now.getTime() - now.getTimezoneOffset() * 60000;
                self.__chart_series[0].data.push([now, cpu_load]);
                self.__draw_chart();
            },
            'json'
        );
    }

    this.__get_chart_data = function(callback) {
        $.get(
            '/api/computer_info/processor.load_stats[]',
            function(data) {
                self.__chart_series[0].data = data['processor.load_stats[]'];
                if(callback) {
                    callback();
                }
            },
            'json'
        );
    }

    this.__init_chart = function() {
        self.__chart_plot = $.plot(self.__chart_container, self.__chart_series, {
            grid: {
                borderWidth: 1,
                minBorderMargin: 20,
                labelMargin: 10,
                backgroundColor: {
                    colors: ["#fff", "#e4f4f4"]
                },
                margin: {
                    top: 8,
                    bottom: 20,
                    left: 20
                },
                markings: function(axes) {
                    var markings = [];
                    var xaxis = axes.xaxis;
                    for (var x = Math.floor(xaxis.min); x < xaxis.max; x += xaxis.tickSize * 2) {
                        markings.push({
                            xaxis: {
                                from: x,
                                to: x + xaxis.tickSize
                            },
                            color: "rgba(232, 232, 255, 0.2)"
                        });
                    }
                    return markings;
                }
            },
            xaxis: {
                mode: "time",
                show: false
            },
            yaxis: {
                min: 0,
                max: 110
            },
            legend: {
                show: true
            }
        });
    }

    this.__draw_chart = function() {
        self.__chart_plot.setData(self.__chart_series);
        self.__chart_plot.setupGrid();
        self.__chart_plot.draw();
    }

}
