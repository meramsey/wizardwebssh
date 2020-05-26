import logging
import os
import sys
import socket
from contextlib import closing
import tornado.web
import tornado.ioloop
from tornado.options import options
from wizardwebssh import handler
from wizardwebssh.handler import IndexHandler, WsockHandler, NotFoundHandler
from wizardwebssh.settings import (
    get_app_settings, get_host_keys_settings, get_policy_setting,
    get_ssl_context, get_server_settings, check_encoding_setting
)

try:
    def find_free_port():
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('127.0.0.1', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            free_port = s.getsockname()[1]
            print("Found free port:" + str(free_port))
            wizardwebsshport = os.path.abspath(os.path.dirname(sys.argv[0])) + "/" + "wizardwebsshport.txt"
            fh = open(wizardwebsshport, "w")
            fh.write(str(free_port))
            fh.close()
            return free_port

except:
       pass

try:
    find_free_port()
except:
    pass

try:
    wizardwebsshport = os.path.abspath(os.path.dirname(sys.argv[0])) + "/" + "wizardwebsshport.txt"
    free_port = open(wizardwebsshport, 'r').read().replace('\n', ' ')
    # print(free_port)
except:
    pass


def make_handlers(loop, options):
    host_keys_settings = get_host_keys_settings(options)
    policy = get_policy_setting(options, host_keys_settings)

    handlers = [
        (r'/', IndexHandler, dict(loop=loop, policy=policy,
                                  host_keys_settings=host_keys_settings)),
        (r'/ws', WsockHandler, dict(loop=loop))
    ]
    return handlers


def make_app(handlers, settings):
    settings.update(default_handler_class=NotFoundHandler)
    return tornado.web.Application(handlers, **settings)


def app_listen(app, free_port, address, server_settings):
    app.listen(free_port, address, **server_settings)
    if not server_settings.get('ssl_options'):
        server_type = 'http'
    else:
        server_type = 'https'
        handler.redirecting = True if options.redirect else False
    logging.info(
        'Listening on {}:{} ({})'.format(address, free_port, server_type)
    )


def main():
    options.parse_command_line()
    check_encoding_setting(options.encoding)
    loop = tornado.ioloop.IOLoop.current()
    app = make_app(make_handlers(loop, options), get_app_settings(options))
    ssl_ctx = get_ssl_context(options)
    server_settings = get_server_settings(options)
    app_listen(app, free_port, options.address, server_settings)
    if ssl_ctx:
        server_settings.update(ssl_options=ssl_ctx)
        app_listen(app, free_port, options.ssladdress, server_settings)
    loop.start()

if __name__ == '__main__':
    main()
