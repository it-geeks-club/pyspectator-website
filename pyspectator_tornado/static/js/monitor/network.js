$(function() {

    var network_info_updater = new NetworkInfoUpdater({
        label_bytes_sent: '#bytes_sent',
        label_bytes_recv: '#bytes_recv',
        interval: 3000
    });
    network_info_updater.start_updating();

});


function NetworkInfoUpdater(params) {

    var self = this;

    this.__label_bytes_sent = $(params.label_bytes_sent);

    this.actual_bytes_sent = null;

    this.__label_bytes_recv = $(params.label_bytes_recv);

    this.actual_bytes_recv = null;

    this.interval = params.interval;

    this.start_updating = function() {
        setTimeout(
            function() { setInterval(self.__update, self.interval); },
            self.interval
        );
    }

    this.__update = function() {
        $.getJSON('/api/comp_info/nif/bytes_sent', function(bytes_sent) {
            if(self.actual_bytes_sent !== bytes_sent) {
                self.actual_bytes_sent = bytes_sent;
                self.__label_bytes_sent.text(bytes_sent);
            }
        });
        $.getJSON('/api/comp_info/nif/bytes_recv', function(bytes_recv) {
            if(self.actual_bytes_recv !== bytes_recv) {
                self.actual_bytes_recv = bytes_recv;
                self.__label_bytes_recv.text(bytes_recv);
            }
        });
    }

}