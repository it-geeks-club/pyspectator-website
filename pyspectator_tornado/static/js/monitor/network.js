$(function() {

    network_info_updater = new NetworkInfoUpdater({
        label_bytes_sent: '#bytes_sent',
        label_bytes_recv: '#bytes_recv',
        interval: 3000
    });
    network_info_updater.start_updating();

});


function NetworkInfoUpdater(params) {

    var self = this;

    this.label_bytes_sent = $(params.label_bytes_sent);

    this.label_bytes_recv = $(params.label_bytes_recv);

    this.interval = params.interval;

    this.start_updating = function() {
        setTimeout(
            function() { setInterval(self.update, self.interval) },
            self.interval
        );
    }

    this.update = function() {
        $.ajax({
            url: '/api/computer_info/network_interface.bytes_sent&network_interface.bytes_recv',
            dataType: 'json',
            success: function(data) {
                self.label_bytes_sent.text(data['network_interface.bytes_sent']);
                self.label_bytes_recv.text(data['network_interface.bytes_recv']);
            }
        });
    }

}