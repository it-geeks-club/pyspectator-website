import os
import base64
from enum import IntEnum
from tornado.web import RequestHandler as NativeRequestHandler, Application


class Mode(IntEnum):
    debug = 0
    release = 1


class WebApplication(Application):

    def __init__(self, mode=Mode.debug, address=None, port=None):
        self.address = address
        handlers = [
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
        super().__init__(handlers, **settings)


class RequestHandler(NativeRequestHandler):

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
        self.render('monitor/general.html')


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
        self.render('monitor/network.html')


class AboutPageHandler(RequestHandler):

    def get(self):
        self.render('about.html')