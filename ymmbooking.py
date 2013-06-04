# This is part of coursework of Software Engineering, 2013.02-2013.07
# Source code by Pengyu CHEN (cpy.prefers.you[at]gmail.com)
# COPYLEFT, ALL WRONGS RESERVED

import bottle
import json
import sqlite3
import sys
import os

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

        # to ensure all these entries are exising in the self.config.file
        # or at least one of the following parseings would fail 
        self.database_path  = parser.get('Path', 'database_path')
        self.db_schema_path = parser.get('Path', 'db_schema_path')
        self.static_path    = parser.get('Path', 'static_path')
        self.view_path      = parser.get('Path', 'view_path')
        self.template_path  = parser.get('Path', 'template_path')
        self.debug  = parser.getboolean('Misc', 'debug')


class Database(object):
    def __init__(self, dbpath, config):
        self.config = config
        self.conn = sqlite3.connect(config.database_path)
    def __del__(self):
        self.conn.close()
    def reset(self):
        config = self.config
        self.conn.close()
        os.remove(config.database_path)
        self.conn = sqlite3.connect(config.database_path)
        if True:
            # well i shall try: and except: here..
            f = open(config.db_schema_path, 'r')
            script = f.read()
            f.close()
            self.conn.executescript(script)
            from data.flight_import import flight_import as fimport
            fimport(config.database_path, "./data/fetched_flights")
            del fimport

class App(object):
    app = bottle.Bottle()
    config = Config('./config.cfg')
    db = Database(config.database_path, config)
    
    def __init__(self):
        #self.app = bottle.Bottle()
        if self.config.debug:
            self.db.reset()
        pass

    def auth_validate(func):
        def decorator(*args, **kwargs):
            # validation here
            return func(*args, **kwargs)
        return decorator

    # routes static css/img/js files
    @app.route('/<category:re:(css|img|js)>/<filepath:path>')
    def static_css_img_js(category, filepath):   
        return bottle.static_file(category + "/" + filepath, root=self.config.static_path)

    @app.route('/')
    @app.route('/index')
    @bottle.view(config.template_path + 'index.tpl')
    @auth_validate
    def index():
        return {}

    @app.get('/flight/search')
    @bottle.view(config.template_path + 'flight/search.tpl')
    def flight_search():
        return {}
    
    @app.get('/flight/search/async')
    def flight_search_json():
        departure_city = bottle.request.query.get('depature_city')
        return { 'flight': [["A", "B", "C"], ["D", "E", "F"]] }

    # following are samples of flight/oneway

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

if __name__ == '__main__':
    application = App()
    bottle.run(application.app, host='localhost', port=8080, debug=True)

