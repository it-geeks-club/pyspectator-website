import os
from tornado import autoreload
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer


class WebServer(object):

    @staticmethod
    def enable_autoreload(ioloop, watch_dirs=list()):
        for current_dir in watch_dirs:
            if not os.path.isdir(current_dir):
                continue
            for (path, dirs, files) in os.walk(current_dir):
                for item in files:
                    autoreload.watch(os.path.join(path, item))
        autoreload.start(ioloop)

    @staticmethod
    def run(web_app):
        # Create http server
        http_server = HTTPServer(web_app)
        if web_app.address is None:
            http_server.listen(web_app.port, address=web_app.address)
        else:
            http_server.listen(web_app.port)
        # Init web server
        ioloop = IOLoop.instance()
        # Add autoreload if this option enabled in settings
        if web_app.settings['autoreload'] is True:
            WebServer.enable_autoreload(ioloop, [web_app.settings['template_path'], ])
        # Start web server
        ioloop.start()
