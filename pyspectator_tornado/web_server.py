import os
import signal
from tornado import autoreload
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer


class WebServer(object):

    def __init__(self, web_app):
        self.web_app = web_app
        self.__io_loop = None
        self.__is_alive = False

    @property
    def is_alive(self):
        return self.__is_alive

    def __on_shutdown(self):
        # Stop pyspectator
        self.web_app.comp_info.stop_monitoring()
        # Stop event loop
        self.__io_loop.stop()

    def enable_autoreload(self, watch_dirs=list()):
        for current_dir in watch_dirs:
            if not os.path.isdir(current_dir):
                continue
            for (path, dirs, files) in os.walk(current_dir):
                for item in files:
                    autoreload.watch(os.path.join(path, item))
        autoreload.start(self.__io_loop)

    def run(self):
        # Server is already running
        if self.is_alive:
            return True
        # Mark server as alive
        self.__is_alive = True
        # Create http server
        http_server = HTTPServer(self.web_app)
        if self.web_app.address is None:
            http_server.listen(self.web_app.port, address=self.web_app.address)
        else:
            http_server.listen(self.web_app.port)
        # Init web server
        self.__io_loop = IOLoop.instance()
        # Add autoreload if this option enabled in settings
        if self.web_app.settings['autoreload'] is True:
            self.enable_autoreload([self.web_app.settings['template_path'], ])
        # Add shutdown handler
        signal.signal(
            signal.SIGINT,
            lambda sig, frame: self.__io_loop.add_callback_from_signal(self.__on_shutdown)
        )
        # Start pyspectator
        self.web_app.comp_info.start_monitoring()
        # Start event loop
        self.__io_loop.start()
