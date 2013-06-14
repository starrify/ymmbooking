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

        # to ensure all these entries are exising in the config file
        # or at least one of the following parseings would fail 
        self.database_path  = parser.get('Path', 'database_path')
        self.db_schema_path = parser.get('Path', 'db_schema_path')
        self.static_path    = parser.get('Path', 'static_path')
        self.view_path      = parser.get('Path', 'view_path')
        self.template_path  = parser.get('Path', 'template_path')
        self.debug  = parser.getboolean('Misc', 'debug')


class Database(object):
    """A wrapper for accessing the database."""

    def __init__(self, config):
        self._config = config
        self._conn = sqlite3.connect(self._config.database_path)
        self._conn.row_factory = Database.dict_factory

    def __del__(self):
        self._conn.close()

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    @staticmethod
    def reset(config):
        print("Started resetting database.")
        try:
            os.remove(config.database_path)
            f = open(config.db_schema_path, 'r')
            script = f.read()
            f.close()
            conn = sqlite3.connect(config.database_path)
            conn.executescript(script)
            conn.commit()
            from data.data_import import data_import as dimport
            dimport(os.path.abspath(config.database_path))
            del dimport
        except None:
            pass
        print("Finished resetting database.")

    def get_airport_by_city(self, city):
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM airport WHERE city_cn LIKE ?", ["%" + city + "%"])
        airports = cursor.fetchall()
        cursor.close()
        return airports

    def get_flights(self, departure_airport="", arrival_airport=""):
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM flight "
            "WHERE depatureAirport=? AND arrivalAirport=?",
            [departure_airport, arrival_airport])
        flights = cursor.fetchall()
        cursor.close()
        return flights

    def get_airline_by_code(self, code=""):
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM airline WHERE code=?", [code])
        airline = cursor.fetchall()
        cursor.close()
        return airline

class App(object):
    """The main application."""
    def __init__(self, config_path='./config.cfg'):
        self._config = Config(config_path)
        #self.app = bottle.Bottle()
        if self._config.debug:
            Database.reset(self._config)
        pass

    @property
    def config(self):
        return self._config

class Misc(object):
    """Miscellaneous items goes here."""
    @staticmethod
    def auth_validate(func):
        def decorator(*args, **kwargs):
            # validation here
            return func(*args, **kwargs)
        return decorator

    @staticmethod
    def unicodify(string, code):
        return bytes(map(ord, string)).decode(code)

app = App('./config.cfg')
bottle_app = bottle.Bottle()

# routes static css/img/js files
@bottle_app.route('/<category:re:(css|img|js)>/<filepath:path>')
def static_css_img_js(category, filepath):   
    return bottle.static_file(category + "/" + filepath, root=app.config.static_path)

@bottle_app.route('/')
@bottle_app.route('/index')
#@bottle_app.route('/spcart')
#@bottle_app.route('/payment')
@bottle.view(app.config.template_path + 'index.html')
#@bottle.view(app.config.template_path + 'spcart.html')
#@bottle.view(app.config.template_path + 'payment.html')
@Misc.auth_validate

def index():
    return {}


@bottle_app.get('/flight/search')
@bottle.view(app.config.template_path + 'flight/search.html')
def flight_search():
    return {}

@bottle_app.get('/order')
@bottle.view(app.config.template_path + 'order.html')
def flight_search():
    return {}

@bottle_app.get('/payment')
@bottle.view(app.config.template_path + 'payment.html')
def flight_search():
    return {}

@bottle_app.get('/trade/booking_history')
@bottle.view(app.config.template_path + 'trade/booking_history.html')
def flight_search():
    return {}

@bottle_app.get('/trade/remark')
@bottle.view(app.config.template_path + 'trade/remark.html')
def flight_search():
    return {}

@bottle_app.get('/flight/search/async')
def flight_search_json():
    d_city, a_city, d_date = list(map(
        bottle.request.query.get, 
        ['departure_city', 'arrival_city', 'departure_date']))

    if not all([d_city, a_city, d_date]):
        return { 'flight': [] }

    d_city, a_city, d_date = list(map(
        lambda x: Misc.unicodify(x, 'utf8'), [d_city, a_city, d_date]))

    db = Database(app.config)
    
    # get airports belong to city
    d_airports = db.get_airport_by_city(d_city)
    a_airports = db.get_airport_by_city(a_city)

    # get flights between airports
    ret_flights = []
    for d_airport in d_airports:
        for a_airport in a_airports:
            flights = db.get_flights(d_airport['code'], a_airport['code'])
            for flight in flights:
                airline = db.get_airline_by_code(flight['flightNumber'][:2])[0]
                ret_flights.append(list(flight.values())
                    + [d_airport['name_cn'], a_airport['name_cn'], airline['name_cn']])
    
    return { 'flight': ret_flights }

# following are samples of flight/oneway

@bottle_app.get('/flight/oneway')
@bottle.view(app.config.template_path + 'flight/oneway.html')
def oneway_get():
    d = { 
        "a1": "Airport 1", 
        "a2": "Airport 2", 
        "dt1": "Datetime 1", 
        "dt2": "Datetime 2",
        "fn": "FlightNo",
    }
    return {'flights': [d, d]}

@bottle_app.get('/flight/oneway_async')
@bottle.view(app.config.template_path + 'flight/oneway_async.html')
def oneway_async_get():
    return {}

@bottle_app.get('/flight/oneway_async_json')
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
    bottle.run(bottle_app, host='localhost', port=8080, debug=True)
    #bottle.run(bottle_app, server='cherrypy', host='localhost', port=8080, debug=True)

