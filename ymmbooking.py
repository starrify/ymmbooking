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
        self._conn.commit()
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
            conn.execute("PRAGMA journal_mode = wal;")
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
        cursor.execute("SELECT * FROM airport WHERE city_cn LIKE ?;", ["%"+city+"%"])
        airports = cursor.fetchall()
        cursor.close()
        return airports

    def get_flights(self, departure_airport="", arrival_airport=""):
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM flight "
            "WHERE departureAirport=? AND arrivalAirport=?;",
            [departure_airport, arrival_airport])
        flights = cursor.fetchall()
        cursor.close()
        return flights

    def get_hotels(self, name="", description="", location="", h_id=None):
        if h_id:
            try:
                h_id = int(h_id)
            except:
                return []
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM hotel "
            "WHERE name LIKE ? AND description LIKE ? AND location LIKE ?;",
            ["%"+name+"%", "%"+description+"%", "%"+location+"%"])
        hotels = cursor.fetchall()
        cursor.close()
        if h_id:
            hotels = [hotel for hotel in hotels if hotel['h_id'] == h_id]
        return hotels

    def get_airline_by_code(self, code=""):
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM airline WHERE code=?;", [code])
        airline = cursor.fetchall()
        cursor.close()
        return airline

    def add_hotel(self, name="", desc="", location=""):
        cursor = self._conn.cursor()
        cursor.execute("SELECT MAX(h_id) from hotel;")
        try:
            h_id = cursor.fetchall()[0]['MAX(h_id)'] + 1
        except: # the table may be empty
            h_id = 1
        try:
            cursor.execute(
                "INSERT INTO hotel (h_id,name,description,location) "
                "VALUES(?,?,?,?);", [h_id, name, desc, location])
            cursor.close()
            return True, h_id
        except:
            return False, -1

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
        if not string:
            return ""
        return bytes(map(ord, string)).decode(code)

app = App('./config.cfg')
bottle_app = bottle.Bottle()

# routes static css/img/js files
@bottle_app.route('/<category:re:(css|img|js)>/<filepath:path>')
def static_css_img_js(category, filepath):   
    return bottle.static_file(category + "/" + filepath, root=app.config.static_path)

@bottle_app.route('/')
@bottle_app.route('/index')
@bottle.view(app.config.template_path + 'index.html')
@Misc.auth_validate
def index():
    return {}

@bottle_app.get('/flight/search')
@bottle.view(app.config.template_path + 'flight/search.html')
def flight_search():
    return {}

@bottle_app.get('/flight/search/async')
def flight_search_json():
    d_city, a_city, d_date, way, non_stop, rate = list(map(
        bottle.request.query.get, 
        ['departure_city', 'arrival_city', 'departure_date', 'way', 'non_stop', 'rate']))

    if not all([d_city, a_city, d_date]):
        return {'flight': []}

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
                flight_lst = [
                    airline['name_cn'],
                    flight['departureTime'],
                    flight['arrivalTime'],
                    d_airport['city_cn'],
                    a_airport['city_cn'],
                    "%.2f"%flight['price'],
                    flight['fuelTax'],
                    flight['airportTax'],
                    flight['flightNumber'],
                    flight['aircraftType'],
                    flight['stop'],
                    0,
                    0,
                ]
                ret_flights.append(flight_lst)
    
    return {'flight': ret_flights}

@bottle_app.get('/trade/remark_history')
@bottle.view(app.config.template_path + 'trade/remark_history.html')
def order():
    return {}

@bottle_app.get('/hotel/search')
@bottle.view(app.config.template_path + 'hotel/search.html')
def flight_search():
    return {}

@bottle_app.get('/hotel/search/async')
def hotel_search_json():
    param = list(map(bottle.request.query.get, 
        ['name', 'description', 'location', 'h_id']))

    if not any(param):
        return {'hotel': []}

    param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))

    db = Database(app.config)
    hotels = db.get_hotels(param[0], param[1], param[2], param[3])
    return {'hotel': [list(hotel.values()) for hotel in hotels]}

@bottle_app.get('/order')
@bottle.view(app.config.template_path + 'order.html')
def order():
    return {}

@bottle_app.get('/trade/booking_history')
@bottle.view(app.config.template_path + 'trade/booking_history.html')
def booking_history():
    return {}

@bottle_app.get('/trade/comment')
@bottle.view(app.config.template_path + 'trade/comment.html')
def trade_remark():
    return {}

@bottle_app.get('/manage/hotel/async')
def hotel_manage_json():
    access_type = bottle.request.query.get('type')
    if access_type == 'add':
        param = list(map(bottle.request.query.get, 
            ['name', 'description', 'location']))
        if not any(param):
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success, h_id = db.add_hotel(param[0], param[1], param[2])
        if success:
            return {'status': 'succeeded', 'h_id': h_id}
    elif access_type == 'update':
        pass
    elif access_type == 'delete':
        pass
    elif access_type == 'search':
        return hotel_search_json()
    return {'status': 'failed'}

if __name__ == '__main__':
    bottle.run(bottle_app, host='0.0.0.0', port=8080, debug=True)
    #bottle.run(bottle_app, server='cherrypy', host='localhost', port=8080, debug=True)

