$(function() {

    var uptime_updater = new UptimeUpdater({
        label_uptime: '#uptime',
        interval: 1000
    });
    uptime_updater.start_updating();

});


function UptimeUpdater(params) {

    var self = this;

    this.label_uptime = $(params.label_uptime);

    this.interval = params.interval;

    this.uptime = 0;

    this.datetime_format = '{Days?} {hh}:{mm}:{ss}';

    this.start_updating = function() {
        self.uptime = parseInt(self.label_uptime.attr('data-init-value'));
        setTimeout(
            function() { setInterval(self.update, self.interval); },
            self.interval
        );
    }

    this.update = function() {
        self.uptime += 1;
        formatted_uptime = jintervals(self.uptime, self.datetime_format);
        self.label_uptime.text(formatted_uptime);
    }
}