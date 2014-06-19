$(function() {
    var uptime_updater = new UptimeUpdater('#uptime', 1000);
    uptime_updater.init();

});

function UptimeUpdater(el, interval) {

    var self = this;

    this.el = $(el);

    this.interval = interval;

    this.uptime = 0;

    this.datetime_format = '{Days?} {hh}:{mm}:{ss}';

    this.init = function() {
        self.uptime = parseInt(self.el.attr('data-init-value'));
        setTimeout(
            function() { setInterval(self.update, self.interval); },
            self.interval
        );
    }

    this.update = function() {
        self.uptime += 1;
        formatted_uptime = jintervals(self.uptime, self.datetime_format);
        self.el.text(formatted_uptime);
    }
}