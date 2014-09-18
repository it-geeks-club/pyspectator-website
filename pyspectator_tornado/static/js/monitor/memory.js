$(function() {

    var mem_info_updater = new MemInfoUpdater({
        label_mem_available: '#available',
        label_mem_used_percent: '#used-percent',
        chart_container: '#used-percent-chart',
        interval: 500
    });
    mem_info_updater.start_updating();

});


function MemInfoUpdater(params) {

    var self = this;

    this.__label_mem_available = $(params.label_mem_available);

    this.__label_mem_used_percent = $(params.label_mem_used_percent);

    this.__chart_container = $(params.chart_container);

    this.__chart_series = [{
        data: [],
        lines: {
            fill: true
        },
        shadowSize: 0
    }];

    this.__chart_data_size = 100;

    this.__chart_plot = null;

    this.actual_mem_available = null;

    this.actual_mem_used_percent = null;

    this.interval = params.interval;

    this.__updating_chart_interval = params.interval * 2;

    this.start_updating = function() {
        self.__get_chart_data(function() {
            self.__init_chart();
            self.__draw_chart();
            self.__start_updating_chart();
        });
        setTimeout(
            function() { setInterval(self.__update, self.interval); },
            self.interval
        );
    }

    this.__start_updating_chart = function() {
        self.__add_chart_value(self.actual_mem_used_percent);
        self.__draw_chart();
        setTimeout(self.__start_updating_chart, self.__updating_chart_interval);
    }

    this.__update = function() {
        $.getJSON('/api/comp_info/mem/available', function(mem_available) {
            if((mem_available !== null) && (self.actual_mem_available !== mem_available)) {
                self.actual_mem_available = mem_available;
                self.__label_mem_available.text(mem_available);
            }
        });
        $.getJSON('/api/comp_info/mem/used_percent', function(mem_used_percent) {
            if((mem_used_percent !== null) && (self.actual_mem_used_percent !== mem_used_percent)) {
                self.actual_mem_used_percent = mem_used_percent;
                self.__label_mem_used_percent.text(mem_used_percent);
            }
        });
    }

    this.__get_chart_data = function(callback) {
        $.getJSON('/api/comp_info/mem/used_percent_stats', function(chart_data) {
            if(chart_data.length < self.__chart_data_size) {
                var filled_data = [];
                for(var i=0; i<self.__chart_data_size-chart_data.length; i++) {
                    filled_data.push([i, -1]);
                }
                for(var i=0, key=filled_data.length; i<chart_data.length; i++, key++) {
                    var val = chart_data[i][1];
                    filled_data.push([key, val]);
                }
                chart_data = filled_data;
            }
            self.__chart_series[0].data = chart_data;
            if(callback) {
                callback();
            }
        });
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
                }
            },
            xaxis: {
                show: false
            },
            yaxis: {
                min: 0,
                max: 110
            },
            legend: {
                show: false
            }
        });
    }

    this.__add_chart_value = function(new_value) {
        if(new_value === null) {
            return null;
        }
        var new_data = [];
        for(var i=1; i<self.__chart_data_size; i++) {
            new_data.push([
                i - 1, self.__chart_series[0].data[i][1]
            ]);
        }
        new_data.push([self.__chart_data_size - 1, new_value]);
        self.__chart_series[0].data = new_data;
    }

    this.__draw_chart = function() {
        self.__chart_plot.setData(self.__chart_series);
        self.__chart_plot.draw();
    }

}