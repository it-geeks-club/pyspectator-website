$(function() {
    var disk_dev_info = new DiskDevInfoUpdater({
        container: '[data-block-name="disk_devices"]',
        interval: 5000,
    });
    disk_dev_info.start_updating();
});


function DiskDevInfoUpdater(params) {

    var self = this;

    this.container = $(params.container);

    this.interval = params.interval;

    this.actual_devices = null;

    this.start_updating = function() {
        self.__init();
        setTimeout(
            function() { setInterval(self.__update, self.interval); },
            self.interval
        );
    }

    this.__init = function() {
        delete self.actual_devices;
        self.actual_devices = [];
        self.container.find('[data-block-name ="device"]').each(function() {
            var html_block = $(this);
            var new_device = new DiskDevInfo({
                device: html_block.attr('data-device-name').trim(),
                mountpoint: html_block.find('[data-value-name="mountpoint"]').text().trim(),
                fstype: html_block.find('[data-value-name="fstype"]').text().trim(),
                used: html_block.find('[data-value-name="used"]').text().trim(),
                total: html_block.find('[data-value-name="total"]').text().trim(),
                used_percent: parseInt(
                    html_block.find('[data-value-name="used_percent"]').css('width').replace('%', '').trim()
                )
            });
            self.actual_devices.push(new_device);
        });
    }

    this.__update = function() {
        $.getJSON('/api/comp_info/disk', function(disk_info) {
            devices = [];
            $.each(disk_info, function() {
                var dev = new DiskDevInfo(this);
                devices.push(dev);
            });
            self.__check_for_old(devices);
            self.__check_for_modified(devices);
            self.__check_for_new(devices);
        });
    }

    this.__check_for_old = function(devices) {
        var old_devices = [];
        for(var i=0; i<self.actual_devices.length; i++) {
            var is_old = true;
            for(var j=0; j<devices.length; j++) {
                if(self.actual_devices[i].device === devices[j].device) {
                    is_old = false;
                    break;
                }
            }
            if(is_old) {
                old_devices.push(i);
            }
        }
        $.each(old_devices, function() {
            self.actual_devices[this].delete_html();
            delete self.actual_devices.splice(this, 1);
        });
    }

    this.__check_for_modified = function(devices) {
        $.each(self.actual_devices, function() {
            for(var i=0; i<devices.length; i++) {
                if(this.device === devices[i].device) {
                    if(!this.equals(devices[i])) {
                        this.mountpoint = devices[i].mountpoint;
                        this.fstype = devices[i].fstype;
                        this.used = devices[i].used;
                        this.total = devices[i].total;
                        this.used_percent = devices[i].used_percent;
                        this.update_html();
                    }
                    break;
                }
            }
        });
    }

    this.__check_for_new = function(devices) {
        $.each(devices, function() {
            var is_new = true;
            for(var i=0; i<self.actual_devices.length; i++) {
                if(this.device === self.actual_devices[i].device) {
                    is_new = false;
                    break;
                }
            }
            if(is_new) {
                this.container = self.container;
                this.create_html();
                self.actual_devices.push(this);
            }
        });
    }

}


function DiskDevInfo(params) {

    var self = this;

    this.container = $(params.container);

    this.device = params.device;

    this.mountpoint = params.mountpoint;

    this.fstype = params.fstype;

    this.used = params.used;

    this.total = params.total;

    this.used_percent = parseInt(params.used_percent);

    this.equals = function(another_dev) {
        var eq = (another_dev instanceof DiskDevInfo) && (self.hash() === another_dev.hash());
        return eq;
    }

    this.hash = function() {
        var hash = self.device.hash() +
           self.mountpoint.hash() +
           self.fstype.hash() +
           self.used.hash() +
           self.total.hash() +
           self.used_percent.toString().hash();
        return hash;
    }

    this.__get_mount_point_info = function() {
        var text = '';
        if((self.mountpoint) && (self.mountpoint !== self.device)) {
            text = ' (mounted as "{0}")'.format(self.mountpoint);
        }
        return text;
    }

    this.__get_fstype_info = function() {
        var text = '';
        if(self.fstype) {
            text = ' in the {0} file system'.format(self.fstype);
        }
        return text;
    }

    this.__get_progressbar_status = function () {
        var class_name = 'progress-bar-danger';
        if(self.used_percent <= 50) {
            class_name = 'progress-bar-success';
        }
        else if(self.used_percent <= 75) {
            class_name = 'progress-bar-warning';
        }
        return class_name;
    }

    this.create_html = function() {
        // Main HTML block
        var html_block = $('<div></div>')
            .attr('data-block-name', 'device')
            .attr('data-device-name', self.device)
            .addClass('row');
        // Temporary DOM element
        var temp_el = null;
        // Common information
        var common_disk_info = $('<div></div>').attr('data-block-name', 'common_disk_info').addClass('row');
        temp_el = $('<div></div>')
            .addClass('col-sm-9 col-md-9 col-lg-9')
            .append(
                $('<b></b>').attr('data-value-name', 'device').text(self.device)
            )
            .append(
                $('<span></span>').attr('data-value-name', 'mountpoint').text(self.__get_mount_point_info)
            )
            .append(
                $('<span></span>').attr('data-value-name', 'fstype').text(self.__get_fstype_info)
            );
        common_disk_info.append(temp_el);
        temp_el = $('<div></div>').addClass('col-sm-3 col-md-3 col-lg-3 text-right').append(
            $('<span></span>')
                .addClass('label label-info')
                .append(
                    $('<span></span>').attr('data-value-name', 'used').text(self.used)
                )
                .append(' / ')
                .append(
                    $('<span></span>').attr('data-value-name', 'total').text(self.total)
                )
        );
        common_disk_info.append(temp_el);
        // Device's used memory information
        var used_disk_info = $('<div></div>').attr('data-block-name', 'used_disk_info').addClass('row');
        temp_el = $('<div></div>').addClass('col-sm-12 col-md-12 col-lg-12').append(
            $('<div></div>').addClass('progress progress-striped active').append(function(){
                var progress_bar = $('<div></div>')
                    .addClass('progress-bar')
                    .css('width', self.used_percent.toString() + '%')
                    .attr('data-value-name', 'used_percent');
                progress_bar.addClass(self.__get_progressbar_status);
                return progress_bar;
            })
        );
        used_disk_info.append(temp_el);
        // Fill main HTML block
        html_block.append(common_disk_info).append(used_disk_info);
        // Add HTML block and horizontal line to container
        self.container.append(html_block).append($('<hr>'));
    }

    this.update_html = function() {
        // Main HTML block
        var html_block = self.container.find('[data-device-name="{0}"]'.format(self.device));
        // Common information
        var common_disk_info = html_block.find('[data-block-name="common_disk_info"]');
        // Update information about moundpoint
        common_disk_info.find('[data-value-name="mountpoint"]').text(self.__get_mount_point_info);
        // Update information about files system
        common_disk_info.find('[data-value-name="fstype"]').text(self.__get_fstype_info);
        // Update information about used and total memory
        common_disk_info.find('[data-value-name="used"]').text(self.used);
        common_disk_info.find('[data-value-name="total"]').text(self.total);
        // Update memory usage progress bar
        html_block.find('[data-block-name="used_disk_info"] [data-value-name="used_percent"]')
            .css('width', self.used_percent.toString() + '%')
            .addClass(self.__get_progressbar_status);
    }

    this.delete_html = function() {
        // Main HTML block
        var html_block =  self.container.find('[data-device-name="{0}"]'.format(self.device));
        // Remove horizontal line
        html_block.next('hr').remove();
        // Remove main HTML block
        html_block.remove();
    }

}