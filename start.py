def main():
    import sys
    from pyspectator_tornado.web_server import WebServer
    from pyspectator_tornado.web_app import WebApplication
    from tornado.options import define, options

    # Create command-line parameters
    define(
        'mode',
        default=None,
        help='work mode of Tornado: "debug" or "release"',
        type=str
    )
    define(
        'address',
        default=None,
        help='domain name for monitoring system',
        type=int
    )
    define(
        'port',
        default=None,
        help='run on the given port',
        type=int
    )

    # Parse command line parameters
    options.parse_command_line(sys.argv)
    # Create new web application
    web_app = WebApplication(
        mode=options.mode,
        address=options.address,
        port=options.port
    )
    # Create and run web server with given web application
    server = WebServer(web_app)
    server.run()


if __name__ == '__main__':
    main()