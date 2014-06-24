import os
import base64
from enum import IntEnum
import calendar
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
            (r'/api/computer_info/([a-zA-Z0-9_\.\&\[\]^/]+)', ApiComputerInfo),
            (r'/about', AboutPageHandler),
            (r'.*', PageNotFoundHandler),
        ]
        default_port = 8888
        settings = {
            # Front-end templates dir
            'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            # Path to shared files
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            # Users authorization page
            'login_url': '/auth/login',
            # Salt for encrypt secure cookies
            'cookie_secret': base64.b64encode(
                '42: Answer to the Ultimate Question of Life, the Universe, and Everything'.encode()
            ),
            # The app will watch for changes to its source files and reload itself if some file will changed
            'autoreload': True,
            # Templates will not be cached
            'compiled_template_cache': False,
            # Static file hashes will not be cached
            'static_hash_cache': False,
            # When raises some Exception will be generated an error page including a stack trace
            'serve_traceback': True,
            # Disable cross-site request forgery protection
            'xsrf_cookies': False
        }
        if mode == Mode.release:
            default_port = 80
            settings.update({
                # Templates will be cached
                'compiled_template_cache': True,
                # Static file hashes will be cached
                'static_hash_cache': True,
                # Don't show error page with stack trace when raises some Exception
                'serve_traceback': False,
                # The app don't will watch for changes in its source files
                'autoreload': False,
                # Enable cross-site request forgery protection
                #'xsrf_cookies': True
            })
        self.port = default_port if port is None else port
        self.computer = Computer()
        super().__init__(handlers, **settings)


class RequestHandler(NativeRequestHandler):

    @property
    def computer(self):
        return self.application.computer

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
                val, unit = '{0:.2f}'.format(val), UnitByte.get_name_reduction(unit)
                byte_value = val + unit
        finally:
            return byte_value


class PageNotFoundHandler(RequestHandler):

    def get(self):
        self.render('error/404.html')


class AuthLoginHandler(RequestHandler):

    def get(self):
        self.render('auth/login.html')


class UserProfileHandler(RequestHandler):

    def get(self, username):
        self.render('user/profile.html')


class MonitorGeneralHandler(RequestHandler):

    def get(self):
        self.render('monitor/general.html', computer=self.__get_general_info())

    def __get_general_info(self):
        # Calculate total disk memory
        total_disk_mem = 0
        for dev in self.computer.nonvolatile_memory:
            if isinstance(dev.total, (int, float)):
                total_disk_mem += dev.total
        # General information
        info = {
            'os': self.computer.os,
            'architecture': self.computer.architecture,
            'hostname': self.computer.hostname,
            'cpu_name': self.computer.processor.name,
            'boot_time': self.computer.boot_time,
            'raw_uptime': int(self.computer.raw_uptime.total_seconds()),
            'uptime': self.computer.uptime,
            'total_mem': self._format_bytes(self.computer.virtual_memory.total),
            'total_disk_mem': self._format_bytes(total_disk_mem)
        }
        return info


class MonitorCpuHandler(RequestHandler):

    def get(self):
        self.render('monitor/cpu.html', cpu=self.__get_cpu_info())

    def __get_cpu_info(self):
        cpu_load = self.computer.processor.load
        if cpu_load is None:
            cpu_load = 0
        info = {
            'name': self.computer.processor.name,
            'count': self.computer.processor.count,
            'load': cpu_load
        }
        return info


class MonitorMemoryHandler(RequestHandler):

    def get(self):
        self.render('monitor/memory.html', memory=self.__get_memory_info())

    def __get_memory_info(self):
        used_percent = self.computer.virtual_memory.used_percent
        if used_percent is None:
            used_percent = 0
        info = {
            'total': self._format_bytes(self.computer.virtual_memory.total),
            'available': self._format_bytes(self.computer.virtual_memory.available),
            'used_percent': used_percent
        }
        return info


class MonitorDiskHandler(RequestHandler):

    def get(self):
        self.render('monitor/disk.html', devices=self.__get_disk_info())

    def __get_disk_info(self):
        info = list()
        for dev in self.computer.nonvolatile_memory:
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
        return info


class MonitorNetworkHandler(RequestHandler):

    def get(self):
        self.render('monitor/network.html', network=self.__get_network_info())

    def __get_network_info(self):
        info = {
            'hostname': self.computer.hostname,
            'mac_address': self.computer.network_interface.hardware_address,
            'ip_address': self.computer.network_interface.ip_address,
            'mask': self.computer.network_interface.subnet_mask,
            'gateway': self.computer.network_interface.default_route,
            'bytes_sent': self._format_bytes(self.computer.network_interface.bytes_sent),
            'bytes_recv': self._format_bytes(self.computer.network_interface.bytes_recv)
        }
        return info


class ApiComputerInfo(RequestHandler):

    def initialize(self):
        self.__supported_parameters = {
            'processor.load': lambda: 0 if self.computer.processor.load is None else self.computer.processor.load,

            'processor.load_stats[]': lambda: self.__get_processor_load_stats(),

            'virtual_memory.available': lambda: self._format_bytes(self.computer.virtual_memory.available),

            'virtual_memory.used_percent':
            lambda: 0 if self.computer.virtual_memory.used_percent is None else self.computer.virtual_memory.used_percent,

            'virtual_memory.used_percent_stats[]': lambda: self.__get_virtual_memory_used_percent_stats(),

            'computer.nonvolatile_memory[]': lambda: self.__get_disk_info(),

            'network_interface.bytes_sent': lambda: self._format_bytes(self.computer.network_interface.bytes_sent),

            'network_interface.bytes_recv': lambda: self._format_bytes(self.computer.network_interface.bytes_recv),
        }

    def get(self, args):
        answer = dict()
        params = args.split('&')
        for param in params:
            if param in self.__supported_parameters:
                getter = self.__supported_parameters[param]
                answer[param] = getter()
            else:
                answer[param] = None
        self.write(json_encode(answer))

    def __transform_timetable(self, timetable):
        values = list(timetable.newest_values(100))
        keys = range(len(values))
        collection = list(zip(keys, values))
        return collection

    def __get_processor_load_stats(self):
        stats = self.__transform_timetable(self.computer.processor.load_stats)
        return stats

    def __get_virtual_memory_used_percent_stats(self):
        stats = self.__transform_timetable(self.computer.virtual_memory.used_percent_stats)
        return stats

    def __get_disk_info(self):
        info = list()
        for dev in self.computer.nonvolatile_memory:
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
        return info


class AboutPageHandler(RequestHandler):

    def get(self):
        self.render('about.html')