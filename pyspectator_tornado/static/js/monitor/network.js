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
        $.get(
            '/api/computer_info/network_interface.bytes_sent&network_interface.bytes_recv',
            function(data) {
                var bytes_sent = data['network_interface.bytes_sent'];
                var bytes_recv = data['network_interface.bytes_recv'];
                if(self.actual_bytes_sent !== bytes_sent) {
                    self.actual_bytes_sent = bytes_sent;
                    self.__label_bytes_sent.text(bytes_sent);
                }
                if(self.actual_bytes_recv !== bytes_recv) {
                    self.actual_bytes_recv = bytes_recv;
                    self.__label_bytes_recv.text(bytes_recv);
                }
            },
            'json'
        );
    }

}