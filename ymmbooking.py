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
    def __init__(self, config):
        self.config = config
        self.conn = sqlite3.connect(config.database_path)
        self.conn.row_factory = Database.dict_factory
    def __del__(self):
        self.conn.close()
    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
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
            self.conn.commit()
            from data.data_import import data_import as dimport
            dimport(os.path.abspath(config.database_path))
            del dimport
        self.__init__(config)
    def cursor(self):
        return self.conn.cursor()

class App(object):
    config = Config('./config.cfg')
    db = Database(config)
    
    def __init__(self):
        #self.app = bottle.Bottle()
        if self.config.debug:
            self.db.reset()
        pass

app = App()
bottle_app = bottle.Bottle()

def auth_validate(func):
    def decorator(*args, **kwargs):
        # validation here
        return func(*args, **kwargs)
    return decorator

# routes static css/img/js files
@bottle_app.route('/<category:re:(css|img|js)>/<filepath:path>')
def static_css_img_js(category, filepath):   
    return bottle.static_file(category + "/" + filepath, root=app.config.static_path)

@bottle_app.route('/')
@bottle_app.route('/index')
@bottle.view(app.config.template_path + 'index.tpl')
@auth_validate
def index():
    return {}

@bottle_app.get('/flight/search')
@bottle.view(app.config.template_path + 'flight/search.tpl')
def flight_search():
    return {}

def get_airport_by_city(cursor, city):
    print("city:", city)
    cursor.execute("SELECT * FROM airport WHERE city LIKE ?", ["%" + city + "%"])
    airports = cursor.fetchall()
    return airports

def unicodify(string, code):
    return bytes(map(ord, string)).decode(code)

@bottle_app.get('/flight/search/async')
def flight_search_json():
    d_city = bottle.request.query.get('departure_city')
    a_city = bottle.request.query.get('arrival_city')
    d_date = bottle.request.query.get('departure_date')
    d_city, a_city, d_data = list(
        map(lambda x: unicodify(bottle.request.query.get(x), 'utf8'), 
            ['departure_city', 'arrival_city', 'departure_date']))

    print([d_city, a_city, d_date])

    if not all([d_city, a_city, d_date]):
        return { 'flight': [] }
   
    # get airports belong to city
    cur = app.db.cursor()
    d_airports = get_airport_by_city(cur, d_city)
    a_airports = get_airport_by_city(cur, a_city)
    print(d_airports)
    print(a_airports)

    # get flights between airports
    ret_flights = []
    for d_airport in d_airports:
        for a_airport in a_airports:
            cur.execute(
                "SELECT * FROM flight "
                "WHERE depatureAirport=? AND arrivalAirport=?",
                [d_airport['code'], a_airport['code']])
            flights = cur.fetchall()
            for flight in flights:
                cur.execute("SELECT * FROM airline WHERE code=?", [flight['flightNumber'][:2]])
                airline = cur.fetchone()
                print(flight)
                print(airline)
                ret_flights.append(list(flight.values())
                    + [d_airport['name_cn'], a_airport['name_cn'], airline['name_cn']])
    
    return { 'flight': ret_flights }

# following are samples of flight/oneway

@bottle_app.get('/flight/oneway')
@bottle.view(app.config.template_path + 'flight/oneway.tpl')
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
@bottle.view(app.config.template_path + 'flight/oneway_async.tpl')
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

