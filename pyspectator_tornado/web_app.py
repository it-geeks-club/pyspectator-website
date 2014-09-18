import os
import base64
from enum import IntEnum
from tornado.web import RequestHandler as NativeRequestHandler, Application
from tornado.escape import json_encode
from pyspectator.computer import Computer
from pyspectator.convert import UnitByte


class Mode(IntEnum):
    debug = 0
    release = 1


class WebApplication(Application):

    def __init__(self, mode=Mode.debug, address=None, port=None):
        self.address = address
        handlers = [
            (r'/', MonitorGeneralHandler),
            (r'/auth/login', AuthLoginHandler),
            (r'/user/profile/([a-zA-Z0-9_])+', UserProfileHandler),
            (r'/monitor/general', MonitorGeneralHandler),
            (r'/monitor/cpu', MonitorCpuHandler),
            (r'/monitor/memory', MonitorMemoryHandler),
            (r'/monitor/disk', MonitorDiskHandler),
            (r'/monitor/network', MonitorNetworkHandler),
            (r'/api/comp_info/cpu/load', ApiCpuLoad),
            (r'/api/comp_info/cpu/load_stats', ApiCpuLoadStats),
            (r'/api/comp_info/mem/available', ApiMemAvailable),
            (r'/api/comp_info/mem/used_percent', ApiMemUsedPercent),
            (r'/api/comp_info/mem/used_percent_stats', ApiMemUsedPercentStats),
            (r'/api/comp_info/disk', ApiDisk),
            (r'/api/comp_info/nif/bytes_sent', ApiNifBytesSent),
            (r'/api/comp_info/nif/bytes_recv', ApiNifBytesRecv),
            (r'/about', AboutPageHandler),
            (r'.*', PageNotFoundHandler),
        ]
        default_port = 8888
        settings = {
            # Path to templates
            'template_path': os.path.join(
                os.path.dirname(__file__), 'templates'
            ),
            # Path to shared files
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            # Users authorization page
            'login_url': '/auth/login',
            # Salt for encrypt secure cookies
            'cookie_secret': base64.b64encode(
                '42: Answer to the Ultimate Question of Life, '
                'the Universe, and Everything'.encode()
            ),
            # The app will be watching for changes in source files and
            # reload itself on file change
            'autoreload': True,
            # Templates will not be cached
            'compiled_template_cache': False,
            # Static file will not be cached
            'static_hash_cache': False,
            # When raises some Exception an extended error page will be
            # generated
            'serve_traceback': True,
            # Disable cross-site request forgery protection
            'xsrf_cookies': False
        }
        if mode == Mode.release:
            default_port = 80
            settings.update({
                # Templates will be cached
                'compiled_template_cache': True,
                # Static file will be cached
                'static_hash_cache': True,
                # Don't show error page with stack trace
                # when raises some Exception
                'serve_traceback': False,
                # The app don't will watch for changes in its source files
                'autoreload': False,
                # Enable cross-site request forgery protection
                # 'xsrf_cookies': True
            })
        self.port = default_port if port is None else port
        self.comp_info = Computer()
        super().__init__(handlers, **settings)


class RequestHandler(NativeRequestHandler):

    @property
    def comp_info(self):
        return self.application.comp_info

    @property
    def cpu_info(self):
        return self.comp_info.processor

    @property
    def mem_info(self):
        return self.comp_info.virtual_memory

    @property
    def disk_info(self):
        return self.comp_info.nonvolatile_memory

    @property
    def nif(self):
        return self.comp_info.network_interface

    def get_current_user(self):
        return None

    def write_error(self, status_code, **kwargs):
        if status_code == 403:
            page = 'error/403.html'
        elif status_code == 404:
            page = 'error/404.html'
        elif status_code == 405:
            page = 'error/405.html'
        elif status_code == 500:
            page = 'error/500.html'
        else:
            page = 'error/unknown.html'
        self.render(page)

    def _format_bytes(self, byte_value):
        try:
            if (byte_value is None) or (byte_value == 0):
                byte_value = '0'
            elif isinstance(byte_value, (int, float)):
                val, unit = UnitByte.auto_convert(byte_value)
                byte_value = '{:.2f}'.format(val) + \
                             UnitByte.get_name_reduction(unit)
        finally:
            return byte_value

    def _transform_timetable(self, timetable, count=100):
        values = list(timetable.newest_values(count))
        keys = range(len(values))
        collection = list(zip(keys, values))
        return collection


class PageNotFoundHandler(RequestHandler):

    def get(self):
        self.render('error/404.html')


class AuthLoginHandler(RequestHandler):

    def get(self):
        self.render('auth/login.html')


class UserProfileHandler(RequestHandler):

    def get(self, username):
        self.render('user/profile.html')


class AboutPageHandler(RequestHandler):

    def get(self):
        self.render('about.html')


class MonitorGeneralHandler(RequestHandler):

    def get(self):
        self.render('monitor/general.html', computer=self.__get_general_info())

    def __get_general_info(self):
        # Calculate total disk memory
        total_disk_mem = 0
        for dev in self.disk_info:
            if isinstance(dev.total, (int, float)):
                total_disk_mem += dev.total
        # General information
        info = {
            'os': self.comp_info.os,
            'architecture': self.comp_info.architecture,
            'hostname': self.comp_info.hostname,
            'cpu_name': self.cpu_info.name,
            'boot_time': self.comp_info.boot_time,
            'raw_uptime': int(self.comp_info.raw_uptime.total_seconds()),
            'uptime': self.comp_info.uptime,
            'total_mem': self._format_bytes(self.mem_info.total),
            'total_disk_mem': self._format_bytes(total_disk_mem)
        }
        return info


class MonitorCpuHandler(RequestHandler):

    def get(self):
        self.render('monitor/cpu.html', cpu=self.__get_cpu_info())

    def __get_cpu_info(self):
        info = {
            'name': self.cpu_info.name,
            'count': self.cpu_info.count,
            'load': self.cpu_info.load if self.cpu_info.load else 0
        }
        return info


class MonitorMemoryHandler(RequestHandler):

    def get(self):
        self.render('monitor/memory.html', memory=self.__get_memory_info())

    def __get_memory_info(self):
        if self.mem_info.used_percent is None:
            used_percent = 0
        else:
            used_percent = self.mem_info.used_percent
        info = {
            'total': self._format_bytes(self.mem_info.total),
            'available': self._format_bytes(self.mem_info.available),
            'used_percent': used_percent
        }
        return info


class MonitorDiskHandler(RequestHandler):

    def get(self):
        self.render('monitor/disk.html', devices=self.__get_disk_info())

    def __get_disk_info(self):
        info = list()
        for dev in self.disk_info:
            if dev.used_percent is None:
                used_percent = 0
            else:
                used_percent = dev.used_percent
            info.append({
                'device': dev.device,
                'mountpoint': dev.mountpoint,
                'fstype': dev.fstype,
                'used': self._format_bytes(dev.used),
                'total': self._format_bytes(dev.total),
                'used_percent': used_percent
            })
        return info


class MonitorNetworkHandler(RequestHandler):

    def get(self):
        self.render('monitor/network.html', network=self.__get_network_info())

    def __get_network_info(self):
        info = {
            'hostname': self.comp_info.hostname,
            'mac_address': self.nif.hardware_address,
            'ip_address': self.nif.ip_address,
            'mask': self.nif.subnet_mask,
            'gateway': self.nif.default_route,
            'bytes_sent': self._format_bytes(self.nif.bytes_sent),
            'bytes_recv': self._format_bytes(self.nif.bytes_recv)
        }
        return info


class ApiCpuLoad(RequestHandler):

    def get(self):
        val = self.cpu_info.load if self.cpu_info.load else 0
        self.write(json_encode(val))


class ApiCpuLoadStats(RequestHandler):

    def get(self):
        val = self._transform_timetable(self.cpu_info.load_stats)
        self.write(json_encode(val))


class ApiMemAvailable(RequestHandler):

    def get(self):
        val = self._format_bytes(self.mem_info.available)
        self.write(json_encode(val))


class ApiMemUsedPercent(RequestHandler):

    def get(self):
        val = self.mem_info.used_percent if self.mem_info.used_percent else 0
        self.write(json_encode(val))


class ApiMemUsedPercentStats(RequestHandler):

    def get(self):
        val = self._transform_timetable(self.mem_info.used_percent_stats)
        self.write(json_encode(val))


class ApiDisk(RequestHandler):

    def get(self):
        info = list()
        for dev in self.disk_info:
            used_percent = dev.used_percent
            if used_percent is None:
                used_percent = 0
            info.append({
                'device': dev.device,
                'mountpoint': dev.mountpoint,
                'fstype': dev.fstype,
                'used': self._format_bytes(dev.used),
                'total': self._format_bytes(dev.total),
                'used_percent': used_percent
            })
        self.write(json_encode(info))


class ApiNifBytesSent(RequestHandler):

    def get(self):
        val = self._format_bytes(self.nif.bytes_sent)
        self.write(json_encode(val))


class ApiNifBytesRecv(RequestHandler):

    def get(self):
        val = self._format_bytes(self.nif.bytes_recv)
        self.write(json_encode(val))
