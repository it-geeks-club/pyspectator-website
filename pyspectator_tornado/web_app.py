import os
import base64
from enum import IntEnum
from tornado.web import RequestHandler as NativeRequestHandler, Application
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
        if status_code == 405:
            page = 'error/405.html'
        elif status_code == 404:
            page = 'error/404.html'
        elif status_code == 500:
            page = 'error/500.html'
        else:
            page = 'error/unknown.html'
        self.render(page)


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
        # General information
        info = {
            'os': self.computer.os,
            'architecture': self.computer.architecture,
            'hostname': self.computer.hostname,
            'cpu_name': self.computer.processor.name,
            'boot_time': self.computer.boot_time,
            'uptime': self.computer.uptime
        }
        # Total virtual memory
        try:
            val, unit = UnitByte.auto_convert(self.computer.virtual_memory.total)
            val, unit = '{0:.2f}'.format(val), UnitByte.get_name_reduction(unit)
            total_mem = val + unit
        except:
            total_mem = '0'
        info['total_mem'] = total_mem
        # Total disk memory
        try:
            total_disk_mem = 0
            for dev in self.computer.nonvolatile_memory:
                if isinstance(dev.total, (int, float)):
                    total_disk_mem += dev.total
            val, unit = UnitByte.auto_convert(total_disk_mem)
            val, unit = '{0:.2f}'.format(val), UnitByte.get_name_reduction(unit)
            total_disk_mem = val + unit
        except:
            total_disk_mem = '0'
        info['total_disk_mem'] = total_disk_mem

        return info


class MonitorCpuHandler(RequestHandler):

    def get(self):
        self.render('monitor/cpu.html')


class MonitorMemoryHandler(RequestHandler):

    def get(self):
        self.render('monitor/memory.html')


class MonitorDiskHandler(RequestHandler):

    def get(self):
        self.render('monitor/disk.html')


class MonitorNetworkHandler(RequestHandler):

    def get(self):
        self.render('monitor/network.html', network=self.__get_network_info())

    def __get_network_info(self):
        info = {
            'hostname': self.computer.hostname,
            'mac_address': self.computer.network_interface.hardware_address,
            'ip_address': self.computer.network_interface.ip_address,
            'mask': self.computer.network_interface.subnet_mask,
            'gateway': self.computer.network_interface.default_route
        }
        try:
            val, unit = UnitByte.auto_convert(self.computer.network_interface.bytes_sent)
            val, unit = '{0:.2f}'.format(val), UnitByte.get_name_reduction(unit)
            bytes_sent = val + unit
        except:
            bytes_sent = '0'
        info['bytes_sent'] = bytes_sent
        try:
            val, unit = UnitByte.auto_convert(self.computer.network_interface.bytes_received)
            val, unit = '{0:.2f}'.format(val), UnitByte.get_name_reduction(unit)
            bytes_received = val + unit
        except:
            bytes_received = '0'
        info['bytes_received'] = bytes_received
        return info


class AboutPageHandler(RequestHandler):

    def get(self):
        self.render('about.html')