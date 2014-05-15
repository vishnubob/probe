from flask import Flask
from flask.ext.mako import MakoTemplates, render_template
import flask.ext.mako 
import os
import json
import tornado
import tornado.web
import tornado.wsgi
import tornado.websocket
import sockjs.tornado
import tektronix

DataDirectory = os.path.join(os.path.split(__file__)[0], "data")

TemplateDirectory = os.path.join(DataDirectory, "templates")
JavascriptDirectory = os.path.join(DataDirectory, "javascript")
AppName = "escope"

app = Flask(AppName)
app.template_folder = TemplateDirectory
mako = MakoTemplates(app)

@app.route('/')
def home():
    #lookup = flask.ext.mako._lookup(app)
    #print lookup.__dict__
    return render_template('scope.html')

class SocketHandler(sockjs.tornado.SockJSConnection):
    def send_curve(self):
        data = [8] * 2500
        msg = json.dumps(data)
        self.send(data)

    def on_message(self, message):
        if message == "curve":
            self.send_curve()
    def on_open(self, ev):
        print "Websocket Opened", ev
    def on_close(self):
        print "Websocket closed"

class FileHandler(tornado.web.RequestHandler):
    _cache = {}

    def get(self):
        uri = self.request.uri
        while uri[0] == '/':
            uri = uri[1:]
        if uri not in self._cache:
            uripath = os.path.join(DataDirectory, uri)
            fh = open(uripath)
            self._cache[uri] = fh.read()
        if uri.endswith(".js"):
            self.set_header("Content-Type", 'application/javascript')
        elif uri.endswith(".css"):
            self.set_header("Content-Type", 'text/css')
        return self.write(self._cache[uri])
            
def get_routes(escope_app):
    routes = [
        (r"/javascript/.*", FileHandler),
        (r"/jam/.*", FileHandler),
        (r"/css/.*", FileHandler),
        (r".*", tornado.web.FallbackHandler, {'fallback':escope_app}),
    ]
    return routes

def start_server(port=8000):
    print app.root_path
    app_instance = tornado.wsgi.WSGIContainer(app)
    routes = get_routes(app_instance)
    socket_router = sockjs.tornado.SockJSRouter(SocketHandler, "/socket")
    routes = socket_router.urls + routes
    tornado_server = tornado.web.Application(routes, debug=True)
    tornado_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    tektronix.escope.start_server()

