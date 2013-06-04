# This is part of coursework of Software Engineering, 2013.02-2013.07
# Source code by Pengyu CHEN (cpy.prefers.you[at]gmail.com)
# COPYLEFT, ALL WRONGS RESERVED

import bottle
import json
import sqlite3
import sys

if sys.version_info < (2,5):
    raise NotImplementedError("Well dude, we need Python 2.5+ or Python 3.x")

class Config():
    def __init__(self, config_path='./config.cfg'): 
        try:
            # Python 3
            import configparser
        except:
            # Python 2.5+
            import ConfigParser as configparser
        parser = configparser.ConfigParser()
        parser.read(config_path)

        # the following parsings shall not fail
        self.database_path  = parser.get('Path', 'database_path')
        self.static_path    = parser.get('Path', 'static_path')
        self.view_path      = parser.get('Path', 'view_path')
        self.template_path  = parser.get('Path', 'template_path')

config = Config()

class Database(object):
    def __init__(self, dbpath):
        self.conn = sqlite3.connect(config.database_path)
    def respawn(self):
        pass
    pass


class App(object):
    def __init__(self):
        #self.app = bottle.Bottle()
        pass
    app = bottle.Bottle()

    def auth_validate(func):
        def decorator(*args, **kwargs):
            # validation here
            return func(*args, **kwargs)
        return decorator

    # routes static files
    @app.route('/static/<filepath:path>')
    def static(filepath):   
        return bottle.static_file(filepath, root=config.static_path)

    @app.route('/')
    @app.route('/index')
    @bottle.view(config.template_path + 'index.tpl')
    @auth_validate
    def index():
        return {}

    @app.get('/flight/oneway')
    @bottle.view(config.template_path + 'flight/oneway.tpl')
    def oneway_get():
        d = { 
            "a1": "Airport 1", 
            "a2": "Airport 2", 
            "dt1": "Datetime 1", 
            "dt2": "Datetime 2",
            "fn": "FlightNo",
        }
        return {'flights': [d, d]}

    @app.get('/flight/oneway_async')
    @bottle.view(config.template_path + 'flight/oneway_async.tpl')
    def oneway_async_get():
        return {}

    @app.get('/flight/oneway_async_json')
    def oneway_async_json_get():
        d = { 
            "a1": "Airport 1", 
            "a2": "Airport 2", 
            "dt1": "Datetime 1", 
            "dt2": "Datetime 2",
            "fn": "FlightNo",
            }
        return {"flight": [d,d]}#json.dumps(d)

    @app.get('/flight/oneway_inter')
    @bottle.view(config.template_path + 'flight/oneway_inter.tpl')
    def oneway_inter_get():
        return {}

    @app.get('/flight/roundtrip')
    @bottle.view(config.template_path + 'flight/roundtrip.tpl')
    def roundtrip_get():
        return {}

    @app.get('/flight/roundtrip_inter')
    @bottle.view(config.template_path + 'flight/roundtrip_inter.tpl')
    def roundtrip_inter_get():
        return {}

if __name__ == '__main__':
    application = App()
    bottle.run(application.app, host='localhost', port=8080, debug=True)

