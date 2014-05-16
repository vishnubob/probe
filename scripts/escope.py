from flask import Flask
from flask.ext.mako import MakoTemplates, render_template
import flask.ext.mako 
import re
import os
import json
import tornado
import tornado.web
import tornado.wsgi
import tornado.websocket
import sockjs.tornado
import tektronix
import argparse
import random

import logging
logger = logging.getLogger("textronix.escope")
logger.setLevel(logging.DEBUG)
DataFolder = os.path.join(os.path.split(__file__)[0], "data")
TemplateFolder = "templates"
AppName = "escope"
app = Flask(AppName)

# List all the available Visa instrument
name = "USB0::0x0699::0x0368::C032162::INSTR"
GlobalScope = tektronix.Scope(name)
GlobalScope.write("RS232:BAUD 19200")
GlobalScope = tektronix.Scope(name)
GlobalScope.dat.wid = 2
GlobalScope.dat.enc = "RIB"

@app.route('/')
def home():
    lookup = flask.ext.mako._lookup(app)
    #print lookup.__dict__
    return render_template('scope.html')

class SocketHandler(sockjs.tornado.SockJSConnection):
    curve_re = re.compile("curve(.*)")

    def send_curve(self, channels):
        #data = [[x, random.randint(0, 200)] for x in range(200)]
        msg = []
        for channel_id in channels:
            channel_name = "CH%s" % channel_id
            GlobalScope.dat.sou = channel_name
            curve = list(enumerate(GlobalScope.curve))
            curve = {"data": curve, "label": channel_name}
            msg.append(curve)
        self.send(msg)

    def on_message(self, message):
        m = self.curve_re.match(message)
        if m:
            channels = m.groups()[0]
            channels = map(int, channels.split(','))
            print channels
            self.send_curve(channels)

    def on_open(self, ev):
        print "Websocket Opened", ev
    def on_close(self):
        print "Websocket closed"

class FileCache(dict):
    _instance = None
    
    @classmethod
    def instance(cls):
        if cls._instance == None:
            cls._instance = cls()
        return cls._instance

class FileHandler(tornado.web.RequestHandler):
    def get(self):
        uri = self.request.uri
        filecache = FileCache.instance()
        while uri[0] == '/':
            uri = uri[1:]
        if uri not in filecache:
            uripath = os.path.join(app.data_folder, uri)
            fh = open(uripath)
            filecache[uri] = fh.read()
        if uri.endswith(".js"):
            self.set_header("Content-Type", 'application/javascript')
        elif uri.endswith(".css"):
            self.set_header("Content-Type", 'text/css')
        return self.write(filecache[uri])
            
def get_routes(escope_app):
    routes = [
        (r"/javascript/.*", FileHandler),
        (r"/jam/.*", FileHandler),
        (r"/css/.*", FileHandler),
        (r".*", tornado.web.FallbackHandler, {'fallback':escope_app}),
    ]
    return routes

def start_server(port=8000, data_folder=None):
    app.data_folder = os.path.abspath(data_folder or DataFolder)
    app.template_folder = os.path.join(app.data_folder, TemplateFolder) 
    logmsg = "Starting server on port=%s, data_folder=%s" % (port, app.data_folder)
    logger.info(logmsg)
    mako = MakoTemplates(app)
    app_instance = tornado.wsgi.WSGIContainer(app)
    routes = get_routes(app_instance)
    socket_router = sockjs.tornado.SockJSRouter(SocketHandler, "/socket")
    routes = socket_router.urls + routes
    tornado_server = tornado.web.Application(routes, debug=True)
    tornado_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

def get_cli():
    parser = argparse.ArgumentParser(description='escope flask app.')
    parser.add_argument('-d', '--data_folder', default=None, help='Data folder')
    parser.add_argument('-p', '--port', default=8000, type=int, help='Port')
    return parser.parse_args()

if __name__ == "__main__":
    args = get_cli()
    start_server(**args.__dict__)
