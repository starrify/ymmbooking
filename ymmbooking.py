# This is part of coursework of Software Engineering, 2013.02-2013.07
# Source code by Pengyu CHEN (cpy.prefers.you[at]gmail.com)
# COPYLEFT, ALL WRONGS RESERVED

import bottle
import urllib.request
import urllib.parse
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
        self.secret = parser.get('Misc', 'secret')
        self.cookie_age    = parser.getint('Misc', 'cookie_age')
        
        self.integration_test   = parser.getboolean('Integration', 'integration_test')
        self.main_deploy    = parser.get('Integration', 'main_deploy')
        self.main_timeout   = parser.getint('Integration', 'main_timeout')
        self.login_url      = parser.get('Integration', 'login_url')
        self.order_url      = parser.get('Integration', 'order_url')
        self.pay_url        = parser.get('Integration', 'pay_url')
        self.localhost      = parser.get('Integration', 'localhost')
        #self.integration_test = parser.getboolean('Integration', 'integration_test')

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
        print(departure_airport, arrival_airport)
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM flight "
            "WHERE departureAirport=? AND arrivalAirport=?;",
            [departure_airport, arrival_airport])
        flights = cursor.fetchall()
        cursor.close()
        return flights
    
    # this is exhausting, we may need a cache or a new hotel table attribute?
    def get_hotel_min_price(self, h_id):
        cursor = self._conn.cursor()
        print("qstr in get_hotel_min_price", "SELECT MIN(price) FROM ROOM WHERE h_id = ?", h_id)

        cursor.execute(
            "SELECT MIN(price) FROM ROOM "
            "WHERE h_id = ?",
            [h_id])

        minprice = cursor.fetchall()[0]['MIN(price)']
        cursor.close()
        return minprice

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

        for hotel in hotels:
            hotel['minprice'] = self.get_hotel_min_price(hotel['h_id'])
        return hotels
    
    def get_hotel_rooms(self, h_id=None, roomType=""):
        cond, data = [], []
        if h_id:
            try:
                h_id = int(h_id)
            except:
                return []
            cond.append("h_id=?")
            data.append(h_id)

        if roomType:
            cond.append("roomType=?")
            data.append(roomType)

        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM room "
            "WHERE " + " AND ".join(cond),
            data)
        rooms = cursor.fetchall()
        cursor.close()
        return rooms
    
    def get_airline_by_code(self, code=""):
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM airline WHERE code=?;", [code])
        airline = cursor.fetchall()
        cursor.close()
        return airline
    
    def add_item(self, table, schema, data, pkey_cols, fillpkey = None):
        cursor = self._conn.cursor()
        
        if(fillpkey):
            fillpkey(table, schema, pkey_cols[0], data, cursor)
        
        #print("INSERT INTO %s (%s) VALUES(%s);"%(table, ','.join(schema), ','.join(['?'] * len(schema))), data)
        try:
            cursor.execute("INSERT INTO %s (%s) VALUES(%s);"%(table, ','.join(schema), ','.join(['?'] * len(schema)))
                        , data)
            cursor.close()
        except:
            print(sys.exc_info())
            return False, -1
        
        return True, list(map(lambda x: data[x], pkey_cols))

    def update_item(self, table, schema, data, pkey_cols):
        cursor = self._conn.cursor()
        attr_non_pri = [i for i in range(len(schema)) if i not in pkey_cols]
        try:
            qstr = "UPDATE %s SET %s WHERE %s"%(table, 
                ','.join(map(lambda x: "%s=?"%schema[x], attr_non_pri)),
                " AND ".join(map(lambda x: "%s=?"%schema[x], pkey_cols)))
            print("qstr=", qstr)
            cursor.execute(qstr, [data[attr] for attr in attr_non_pri] +
                [data[attr] for attr in pkey_cols]);
            cursor.close()
            return True
        except:
            print(sys.exc_info())
            return False

    def delete_item(self, table, schema, data, pkey_cols):
        cursor = self._conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM %s WHERE %s"%(table, 
                    ' AND '.join(map(lambda x: "%s=?"%schema[x], pkey_cols)))
                , data) # data consists of primary key values in order
            cursor.close()
            return True
        except:
            return False

    def create_transaction_flight(self, 
        tid="",
        flight_number="", uid="", date="", price="", user_info=None):
        if not user_info:
            user_info = [""] * 7
        if len(user_info) < 7:
            user_info += [""] * 7
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO flightTransaction "
            "VALUES("
                #"NULL," # auto increment
                "?,"
                "?,?,?,?,'not_paid',"
                "?,?,?,?,?,?,?)",
            [tid, flight_number, uid, date, price] + user_info)
        cursor.close()
        return
    
    def create_transaction_hotel(self, 
        tid="",
        h_id="", uid="", date="", price="", user_info=None):
        
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO hotelTransaction "
            "VALUES("
                #"NULL," # auto increment
                "?,"
                "?,?,?,?,'not_paid')",
                #"?,?,?,?,?,?,?)",
            [tid, h_id, uid, date, price]) # + user_info)
        cursor.close()
        return


    # unlike the method for admin, uid must be provided
    def get_user_flight_transaction_history(self, uid="", start_date="", end_date="2999-12-31"):
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM flightTransaction "
            "WHERE u_id = ? AND time BETWEEN ? AND ?",
            [uid, start_date, end_date])
        ret = cursor.fetchall()
        cursor.close()
        return ret

    # uid may be empty here
    def get_flight_transaction_history(self, uid="", start_date="", end_date=""):
        cond, data = [], []
        cursor = self._conn.cursor()
        if uid:
            cond.append("u_id=?")
            data.append(uid)
        if start_date or end_date:
            if not start_date: start_date = "0000-00-00"
            if not end_date: end_date = "2999-12-31"
            cond.append("time BETWEEN ? AND ?")
            data += [start_date, end_date]
        print("SELECT * FROM flightTransaction "
            "WHERE " + " AND ".join(cond), data)

        cursor.execute(
            "SELECT * FROM flightTransaction "
            "WHERE " + " AND ".join(cond),
            data)
        ret = cursor.fetchall()
        cursor.close()
        return ret

    def get_flight_transaction(self, uid="", tid=""):
        try:
            cursor = self._conn.cursor()
            cursor.execute(
                "SELECT * FROM flightTransaction "
                "WHERE u_id=? AND t_id=?",
                [uid, tid])
            ret = cursor.fetchall()
            cursor.close()
            return ret[0]
        except:
            return []
    
    # unlike the method for admin, user id must be provided here
    def get_user_flight_comment(self, uid="", start_date="", end_date="2999-12-31"):
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM flightComment "
            "WHERE u_id = ?",
            [uid])
        ret = cursor.fetchall()
        cursor.close()
        return ret
    
    # unlike the method for admin, uid must be provided
    def get_user_hotel_transaction_history(self, uid="", start_date="", end_date="2999-12-31"):
        cursor = self._conn.cursor()
        print(uid, start_date, end_date)
        cursor.execute(
            "SELECT * FROM hotelTransaction "
            "WHERE u_id = ? AND time BETWEEN ? AND ?",
            [uid, start_date, end_date])
        ret = cursor.fetchall()
        cursor.close()
        return ret

    # uid may be empty here
    def get_hotel_transaction_history(self, uid="", start_date="", end_date=""):
        cond, data = [], []
        cursor = self._conn.cursor()
        if uid:
            cond.append("u_id=?")
            data.append(uid)
        if start_date or end_date:
            if not start_date: start_date = "0000-00-00"
            if not end_date: end_date = "2999-12-31"
            cond.append("time BETWEEN ? AND ?")
            data += [start_date, end_date]

        cursor.execute(
            "SELECT * FROM hotelTransaction "
            "WHERE " + " AND ".join(cond),
            data)
        ret = cursor.fetchall()
        cursor.close()
        return ret

    # unlike the method for admin, u_id must be provided here
    def get_user_hotel_comment(self, uid="", start_date="", end_date=""):
        cond, data = [], []
        cursor = self._conn.cursor()
        
        # oops but date is not yet supported in this table
        #if start_date or end_date:
        #    start_date = start_date if start_date else "0000-00-00"
        #    end_date = end_date if end_date else "2999-12-31"
        #    cond.append("time BETWEEN ? AND ?")
        #    data += [start_date, end_date]
        
        cursor.execute(
            "SELECT * FROM hotelComment "
            "WHERE u_id=?",
            [uid])
        ht_cmt = cursor.fetchall()
        cursor.close()
        return ht_cmt

    def add_flight_comment(self, uid='', flight_number='', message='', rate=''):
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO flightComment "
            "VALUES("
                "NULL," # auto increment
                "?,?,?,?)",
            [flight_number, uid, message, rate])
        cursor.close()
        return

    def set_transaction_status(self, tid='', status=''):
        try:
            cursor = self._conn.cursor()
            cursor.execute(
                "UPDATE flightTransaction "
                "SET status = ? "
                "WHERE t_id = ? ",
                [status, tid])
            cursor.execute(
                "UPDATE hotelTransaction "
                "SET status = ? "
                "WHERE t_id = ? ",
                [status, tid])
            cursor.close()
        except:
            pass
        return

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
            uid = bottle.request.get_cookie('uid', secret=app.config.secret)
            if not uid:
                bottle.redirect('/login?redirect=%s' %urllib.parse.quote(bottle.request.url))
            return func(*args, **kwargs)
        return decorator

    @staticmethod
    def unicodify(string, code):
        if not string:
            return ""
        return bytes(map(ord, string)).decode(code)

    @staticmethod
    def post_new_order(uid, otype, onum, ourl, oprice):
        postdata = urllib.parse.urlencode({
            'buid': uid,
            'type': otype,
            'num': onum,
            'url': ourl,
            'oprice': oprice
        }).encode('utf8')
        order_url = app.config.main_deploy + app.config.order_url
        ret = urllib.request.urlopen(order_url, postdata, app.config.main_timeout)
        jdata = json.loads(json.loads(ret.read().decode('utf8')))
        print(jdata)
        return jdata['err'], jdata['oid']

app = App('./config.cfg')
bottle_app = bottle.Bottle()

# routes static css/img/js files
@bottle_app.route('/<category:re:(css|img|js)>/<filepath:path>')
def static_css_img_js(category, filepath):   
    return bottle.static_file(category + "/" + filepath, root=app.config.static_path)

@bottle_app.route('/')
@bottle.view(app.config.template_path + 'index.html')
def index():
    return {}

@bottle_app.route('/login')
@bottle.view(app.config.template_path + 'login.html')
def login():
    """Merely a test login form"""
    redirect_url = bottle.request.query.get('redirect')
    if not redirect_url:
        redirect_url = '/'
    return {'redirect_url': redirect_url}

@bottle_app.post('/auth')
def auth():
    """Merely for testing for now"""
    uid = ''
    param = list(map(bottle.request.forms.get, ['username', 'passwd', 'group']))
    param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
    # poor compatibility layer....
    if param[2] == 'user':
        param[2] = '1'
    elif param[2] == 'admin':
        param[2] = '2'
    elif param[2] == 'auditor':
        param[2] = '3'
    if app.config.integration_test:
        """stupid API from group 1"""
        postdata = urllib.parse.urlencode({'username': param[0], 'password': param[1], 'group': param[2]}).encode('utf8')
        try:
            auth_url = app.config.main_deploy + app.config.login_url
            ret = urllib.request.urlopen(auth_url, postdata, app.config.main_timeout)
            jdata = json.loads(json.loads(ret.read().decode('utf8')))
            print(jdata)
            if jdata['err'] == "100":
                uid = jdata['uid']
            else:
                return "Authentication failed."
        except None:
            return "Error communicating with auth API by group 1"
            pass
    else:
        """authentication always pass"""
        uid = param[0]
        pass
    bottle.response.set_cookie('uid', uid, secret=app.config.secret, max_age=app.config.cookie_age)
    bottle.response.set_cookie('username', param[0], max_age=app.config.cookie_age)
    redirect_url = bottle.request.forms.get('redirect')
    if not redirect_url:
        redirect_url = '/'
    bottle.redirect(redirect_url)

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
                    d_airport['name_cn'],
                    a_airport['name_cn'],
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

@bottle_app.get('/hotel/search')
@bottle.view(app.config.template_path + 'hotel/search.html')
def flight_search():
    return {}

@bottle_app.get('/hotel/search/async')
def hotel_search_json():
    param = list(map(bottle.request.query.get, 
        ['name', 'description', 'location', 'h_id']))
    if not any(param):
        return {'status': 'failed'}
    param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))

    db = Database(app.config)
    hotels = db.get_hotels(param[0], param[1], param[2], param[3])
    return {'status': 'succeeded', 'hotel': [list(map(lambda x: hotel[x], 
        ('h_id', 'name', 'description', 'location', 'minprice'))) for hotel in hotels]}

@bottle_app.get('/hotel/room/search/async')
def hotel_room_search_json():
    param = list(map(bottle.request.query.get,
        ['h_id', 'roomType'])) # support for these two is enough
    if not any(param):
        return {'status': 'failed'}
    param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))

    db = Database(app.config)
    rooms = db.get_hotel_rooms(param[0], param[1])
    return {'status': 'succeeded', 'room': rooms} 

@bottle_app.get('/hotel/hotel_info')
@bottle.view(app.config.template_path + 'hotel/hotel_info.html')
def hotel_info():
    param = list(map(bottle.request.query.get,
        ['h_id']))
    if not param[0]:
        bottle.redirect('/')
    param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))

    return {
        'h_id': param[0],
    }

@bottle_app.get('/order')
@bottle.view(app.config.template_path + 'order.html')
@Misc.auth_validate
def order():
    o_type = bottle.request.query.get('type')
    if o_type == 'flight':
        param = list(map(bottle.request.query.get, 
            ['flight_number', 'date', 'price']))
        if not any(param):
            bottle.redirect('/')
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        return {
            'item_name': param[0] + '航班: ' + param[1], 
            'item_price': param[2],
            'total_price': param[2], 
            'order_type': 'flight',
            '_item_id': param[0],
            '_item_date': param[1],
            '_item_price': param[2]}
    elif o_type == 'hotel':
        param = list(map(bottle.request.query.get, 
            ['h_id', 'roomType', 'date', 'price']))
        print(param)
        if not any(param):
            bottle.redirect('/')
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        return {
            'item_name': '酒店' + param[0] + ': ' + param[1], 
            'item_price': param[3],
            'total_price': param[3], 
            'order_type': 'hotel',
            '_item_id': param[0],
            '_item_date': param[2],
            '_item_price': param[3]}

    else:   # invalid type or no type.
        #bottle.redirect('/')
        pass
    #bottle.redirect('/')
    return {
        'item_name': '', 'item_price': '', 'total_price': '', 
        'order_type': '', '_item_id':  '', '_item_date': '', '_item_price': ''}

@bottle_app.get('/pay')
@Misc.auth_validate
@bottle.view(app.config.template_path + 'pay.html')
def pay():
    param = list(map(bottle.request.query.get,
        ['t_id', 'item_name', 'item_date', 'item_price']))
    param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))

    return {'_tid': param[0], 'item_name': param[1], 'item_time': param[2], 'item_price': param[3]}

@bottle_app.post('/pay')
@Misc.auth_validate
def pay_post():
    param = list(map(bottle.request.forms.get, ['_tid', 'paypassword']))
    param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
    uid = bottle.request.get_cookie('uid', secret=app.config.secret)
    
    try:
        postdata = urllib.parse.urlencode({
            'type': 0,
            'buid': uid,
            'passwd': param[1],
            'oids[]': param[0]
        }).encode('utf8')
        print(postdata)
        pay_url = app.config.main_deploy + app.config.pay_url
        ret = urllib.request.urlopen(pay_url, postdata, app.config.main_timeout)
        jdata = json.loads(json.loads(ret.read().decode('utf8')))
        print(jdata)
        if jdata['err'] != '300':
            return "Error paying: %s" %jdata['err']
    except:
        return "Error commmunicating with group 2"
        pass
    
    db = Database(app.config)
    db.set_transaction_status(param[0], 'not_commented')
 
    bottle.redirect('/trade/booking_history')
    return

@bottle_app.get('/create_transaction')
@Misc.auth_validate
def create_transaction():
    ct_type = bottle.request.query.get('type')
    if ct_type == 'flight':
        param = list(map(bottle.request.query.get,
            ['_item_id', '_item_date', '_item_price', 
                'is_child', 'user_name', 'ID_type', 'ID_number', 
                'contact_name', 'contact_tel', 'contact_email']))
        if not all(param[:3]):
           bottle.redirect('/trade/booking_history')
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        uid = bottle.request.get_cookie('uid', secret=app.config.secret)
        #try:
        if True:
            err, tid = Misc.post_new_order(uid, 1, 1, app.config.localhost + '/trade/booking_history?type=flight', param[2])
            print(tid)
            if err != '300':
                return "Error creating order"
        #except:
        #    return "Error commmunicating with group 2"
        db = Database(app.config)
        db.create_transaction_flight(tid, param[0], uid, param[1], param[2], param[3:])
        bottle.redirect('/trade/booking_history?type=flight')
    elif ct_type == 'hotel':
        param = list(map(bottle.request.query.get,
            ['_item_id', '_item_date', '_item_price']))
        # it's a pity but our db schema does not support these in hotel
        #                'is_child', 'user_name', 'ID_type', 'ID_number', 
        #                'contact_name', 'contact_tel', 'contact_email']))
        if not all(param[:3]):
            bottle.redirect('/trade/booking_history?type=hotel')
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        uid = bottle.request.get_cookie('uid', secret=app.config.secret)
        try:
            err, tid = Misc.post_new_order(uid, 2, 1, app.config.localhost + '/trade/booking_history?type=hotel', param[2])
            if err != '300':
                return "Error creating order"
        except:
            return "Error commmunicating with group 2"
        db = Database(app.config)
        db.create_transaction_hotel(tid, param[0], uid, param[1], param[2])
        bottle.redirect('/trade/booking_history')
    else:
        pass
    return {}

@bottle_app.get('/trade/booking_history')
@bottle.view(app.config.template_path + '/trade/booking_history.html')
@Misc.auth_validate
def booking_history():
    return {}

@bottle_app.get('/trade/booking_history/async')
@Misc.auth_validate
def booking_history_async():
    search_type = bottle.request.query.get('type')
    if search_type == 'flight':
        uid = bottle.request.get_cookie('uid', secret=app.config.secret)
        param = list(map(bottle.request.query.get,
            ['begin_date', 'end_date']))
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        hist = db.get_user_flight_transaction_history(uid, param[0], param[1])
        ret = []
        for h in hist:
            ret.append([
                h['t_id'], h['flightNumber'], h['time'], h['price'],
                h['status']])
        return {'flights': ret}
    elif search_type == 'hotel':
        uid = bottle.request.get_cookie('uid', secret=app.config.secret)
        param = list(map(bottle.request.query.get,
            ['begin_date', 'end_date']))
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        hist = db.get_user_hotel_transaction_history(uid, param[0], param[1])
        ret = []
        for h in hist:
            ret.append([
                h['t_id'], h['h_id'], h['time'], h['price'], h['status']])
        return {'hotels': ret}
    elif search_type == 'all':
        # well, the code is duplicated, but it is not the issue to be considered now
        uid = bottle.request.get_cookie('uid', secret=app.config.secret)
        param = list(map(bottle.request.query.get,
            ['begin_date', 'end_date']))
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        flighthist = db.get_user_flight_transaction_history(uid, param[0], param[1])
        hotelhist = db.get_user_hotel_transaction_history(uid, param[0], param[1])
        flights, hotels = [], []
        for h in flighthist:
            flights.append([
                h['t_id'], h['flightNumber'], h['time'], h['price'],
                h['status']])
        for h in  hotelhist:
            hotels.append([
                h['t_id'], h['h_id'], h['time'], h['price']])
        return {'flights': flights, 'hotels': hotels}
    else:
        pass
    return {}

@bottle_app.get('/trade/comment')
@bottle.view(app.config.template_path + 'trade/comment.html')
@Misc.auth_validate
def trade_comment():
    comment_type = bottle.request.query.get('type')
    if comment_type == 'flight':
        uid = bottle.request.get_cookie('uid', secret=app.config.secret)
        tid = bottle.request.query.get('tid')
        tid = Misc.unicodify(tid, 'utf8')
        db = Database(app.config)
        trans = db.get_flight_transaction(uid, tid)
        if not trans: # error accessing database
            bottle.redirect('/trade/booking_history')
        #if not trans['status'] == 'paid':
        #    bottle.redirect('/trade/booking_history')
        return {'_tid': tid, '_item_id': trans['flightNumber'], 
            'item_id': trans['flightNumber'], 'user_name': trans['user_name'],
            'time': trans['time'], 'price': trans['price']}
        
    elif comment_type == "hotel":
        bottle.redirect("/trade/booking_history")
    else:
        #bottle.redirect('/trade/booking_history')
        pass
    return {}

@bottle_app.get('/trade/comment/submit')
@bottle.view(app.config.template_path + 'trade/comment.html')
@Misc.auth_validate
def comment_submit():
    comment_type = bottle.request.query.get('type')
    if comment_type == 'flight':
        uid = bottle.request.get_cookie('uid', secret=app.config.secret)
        param = list(map(bottle.request.query.get,
            ['_tid', '_item_id', 'message', 'rate']))
        if not param[1]:
            bottle.redirect("/trade/booking_history")
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        db.add_flight_comment(uid, param[1], param[2], param[3])
        bottle.redirect("/trade/comment_history")
    elif comment_type == "hotel":
        pass
    else:
        #bottle.redirect('/trade/booking_history')
        pass
    bottle.redirect("/trade/booking_history")


@bottle_app.get('/trade/comment_history')
@bottle.view(app.config.template_path + 'trade/comment_history.html')
@Misc.auth_validate
def trade_remark():
    return {}

@bottle_app.get('/trade/comment_history/async')
@Misc.auth_validate
def comment_history_asycn():
    comment_type = bottle.request.query.get('type')
    if comment_type == 'flight':
        uid = bottle.request.get_cookie('uid', secret=app.config.secret)
        param = list(map(bottle.request.query.get,
            ['begin_date', 'end_date']))
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        raw_comments = db.get_user_flight_comment(uid, param[0], param[1])
        comments = [[
            comment['c_id'], comment['flightNumber'], comment['u_id'], 
            comment['message'], comment['rate']] for comment in raw_comments]
        return {'comments': comments}
    elif comment_type == "hotel":
        pass
    else:
        pass
    
    return {'comments': []}

#default primary key filler, assume autoinc on col 0
def fillpkey_autoinc(table, schema, col, data, cursor):    
    cursor.execute("SELECT MAX(%s) from %s;"%(schema[col], table))
    try:
        pkey = cursor.fetchall()[0]['MAX(%s)'%schema[col]] + 1
    except: # the table may be empty
        pkey = 1
    data[col] = pkey
 
@bottle_app.get('/manage/flight/info')
@bottle.view(app.config.template_path + 'manage/flight/flight.html')
@Misc.auth_validate
def manage_flight_info():
    return {}

@bottle_app.get('/manage/flight/info/async')
@Misc.auth_validate
def flight_manage_json():
    schema = ['flightNumber', 'fuelTax', 'airportTax', 'departureAirport', 'departureTime', 'arrivalAirport', 
             'arrivalTime', 'aircraftType', 'schedule', 'punctuality', 'stop', 'price']
    access_type = bottle.request.query.get('type')
    if access_type == 'add':
        param = list(map(bottle.request.query.get, schema))
        if not any(param):
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success, pkey = db.add_item('flight', schema, param, [0])
        if success:
            return {'status': 'succeeded', 'flightNumber': pkey[0]}
    elif access_type == 'update':
        param = list(map(bottle.request.query.get, schema))
        if not param[0]:
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success = db.update_item('flight', schema, param, [0])
        if success:
            return {'status': 'succeeded'}
    elif access_type == 'delete':
        param = list(map(bottle.request.query.get, ['flightNumber']))
        if not param[0]:
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success = db.delete_item('flight', schema, param, [0])
        if success:
            return {'status': 'succeeded'}
    elif access_type == 'search':
        param = list(map(bottle.request.query.get, 
            ['departureCity', 'arrivalCity']))
        if not any(param):
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        
        db = Database(app.config)
        # get airports belong to city
        d_airports = db.get_airport_by_city(param[0])
        a_airports = db.get_airport_by_city(param[1])

        # get flights between airports
        ret_flights = []
        for d_airport in d_airports:
            for a_airport in a_airports:
                ret_flights += db.get_flights(d_airport['code'], a_airport['code'])

        return { 'status': 'succeeded', 'flight': ret_flights }
    return {'status': 'failed'}


@bottle_app.get('/manage/flight/transaction')
@bottle.view(app.config.template_path + 'manage/flight/transaction.html')
@Misc.auth_validate
def manage_flight_transaction():
    return {}

@bottle_app.get('/manage/flight/transaction/async')
@Misc.auth_validate
def flight_transaction_manage_json():
    schema = ['t_id', 'flightNumber', 'u_id', 'time', 'price', 'status', 'is_child', 'user_name',
                    'ID_type', 'ID_number', 'contact_name', 'contact_tel', 'contact_email'];
    access_type = bottle.request.query.get('type')
    if access_type == 'add':
        param = list(map(bottle.request.query.get, schema))
        if not any(param):
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success, pkey = db.add_item('flightTransaction', schema, param, [0], fillpkey_autoinc)
        if success:
            return {'status': 'succeeded', 't_id': pkey[0]}
    elif access_type == 'update':
        param = list(map(bottle.request.query.get, schema))
        if not param[0]:
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success = db.update_item('flightTransaction', schema, param, [0])
        if success:
            return {'status': 'succeeded'}
    elif access_type == 'delete':
        param = list(map(bottle.request.query.get, ['t_id']))
        if not param[0]:
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success = db.delete_item('flightTransaction', schema, param, [0])
        if success:
            return {'status': 'succeeded'}
    elif access_type == 'search':
        param = list(map(bottle.request.query.get, 
            ['u_id', 'beginDate', 'endDate']))
        if not any(param):
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        
        db = Database(app.config)
        trans = db.get_flight_transaction_history(param[0], param[1], param[2])

        return { 'status': 'succeeded', 'flightTransaction': trans }
    return {'status': 'failed'}

@bottle_app.get('/manage/flight/comment')
@bottle.view(app.config.template_path + 'manage/flight/comment.html')
@Misc.auth_validate
def manage_flight_comment():
    return {}

@bottle_app.get('/manage/flight/comment/async')
@Misc.auth_validate
def flight_comment_manage_json():
    schema = ['c_id', 'flightNumber', 'u_id', 'message', 'rate']
    access_type = bottle.request.query.get('type')
    if access_type == 'add':
        param = list(map(bottle.request.query.get, schema))
        if not any(param):
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success, pkey = db.add_item('flightComment', schema, param, [0], fillpkey_autoinc)
        if success:
            return {'status': 'succeeded', 'c_id': pkey[0]}
    elif access_type == 'update':
        param = list(map(bottle.request.query.get, schema))
        if not param[0]:
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success = db.update_item('flightComment', schema, param, [0])
        if success:
            return {'status': 'succeeded'}
    elif access_type == 'delete':
        param = list(map(bottle.request.query.get, ['c_id']))
        if not param[0]:
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success = db.delete_item('flightComment', schema, param, [0])
        if success:
            return {'status': 'succeeded'}
    elif access_type == 'search':
        param = list(map(bottle.request.query.get, 
            ['u_id', 'beginDate', 'endDate']))
        if not any(param):
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        
        db = Database(app.config)
        cmt = db.get_user_flight_comment(param[0], param[1], param[2])

        return { 'status': 'succeeded', 'flightComment': cmt }
    return {'status': 'failed'}

@bottle_app.get('/manage/hotel/info')
@bottle.view(app.config.template_path + 'manage/hotel/hotel.html')
@Misc.auth_validate
def manage_hotel_info():
    return {}

@bottle_app.get('/manage/hotel/info/async')
@Misc.auth_validate
def hotel_manage_json():
    schema = ['h_id', 'name', 'description', 'location']
    access_type = bottle.request.query.get('type')
    if access_type == 'add':
        param = list(map(bottle.request.query.get, schema))
        if not any(param):
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success, pkey = db.add_item('hotel', schema, param, [0], fillpkey_autoinc)
        if success:
            return {'status': 'succeeded', 'h_id': pkey[0]}
    elif access_type == 'update':
        param = list(map(bottle.request.query.get, schema))
        if not param[0]:
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success = db.update_item('hotel', schema, param, [0])
        if success:
            return {'status': 'succeeded'}
    elif access_type == 'delete':
        param = list(map(bottle.request.query.get, ['h_id']))
        if not param[0]:
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success = db.delete_item('hotel', schema, param, [0])
        if success:
            return {'status': 'succeeded'}
    elif access_type == 'search':
        param = list(map(bottle.request.query.get, ['h_id', 'name', 'location']))
        if not any(param):
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        hotels = db.get_hotels(param[1], param[2], '', param[0])
        return {'status': 'succeeded', 'hotel': hotels }
         
    return {'status': 'failed'}

@bottle_app.get('/manage/hotel/room')
@bottle.view(app.config.template_path + 'manage/hotel/room.html')
@Misc.auth_validate
def manage_hotel_room():
    return {}

@bottle_app.get('/manage/hotel/room/async')
@Misc.auth_validate
def room_manage_json():
    schema = ['h_id', 'roomType', 'bedType', 'breakfast', 'wifi', 'price']
    access_type = bottle.request.query.get('type')
    if access_type == 'add':
        param = list(map(bottle.request.query.get, schema))
        if not any(param):
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success, pkey = db.add_item('room', schema, param, [0, 1])
        if success:
            return {'status': 'succeeded', 'h_id': pkey[0], 'roomType': pkey[1]}
    elif access_type == 'update':
        param = list(map(bottle.request.query.get, schema))
        if not param[0]:
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success = db.update_item('room', schema, param, [0, 1])
        if success:
            return {'status': 'succeeded'}
    elif access_type == 'delete':
        param = list(map(bottle.request.query.get, ['h_id', 'roomType']))
        if not param[0]:
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success = db.delete_item('room', schema, param, [0, 1])
        if success:
            return {'status': 'succeeded'}
    elif access_type == 'search':
        param = list(map(bottle.request.query.get, ['h_id', 'roomType']))
        if not any(param):
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        rooms = db.get_hotel_rooms(param[0], param[1])
        return {'status': 'succeeded', 'room': rooms }
         
    return {'status': 'failed'}

@bottle_app.get('/manage/hotel/transaction')
@bottle.view(app.config.template_path + 'manage/hotel/transaction.html')
@Misc.auth_validate
def manage_hotel_transaction():
    return {}

@bottle_app.get('/manage/hotel/transaction/async')
@Misc.auth_validate
def hotel_transaction_manage_json():
    schema = ['t_id', 'h_id', 'u_id', 'time', 'price', 'status']
    access_type = bottle.request.query.get('type')
    if access_type == 'add':
        param = list(map(bottle.request.query.get, schema))
        if not any(param):
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success, pkey = db.add_item('hotelTransaction', schema, param, [0], fillpkey_autoinc)
        if success:
            return {'status': 'succeeded', 't_id': pkey[0]}
    elif access_type == 'update':
        param = list(map(bottle.request.query.get, schema))
        if not param[0]:
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success = db.update_item('hotelTransaction', schema, param, [0])
        if success:
            return {'status': 'succeeded'}
    elif access_type == 'delete':
        param = list(map(bottle.request.query.get, ['t_id']))
        if not param[0]:
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success = db.delete_item('hotelTransaction', schema, param, [0])
        if success:
            return {'status': 'succeeded'}
    elif access_type == 'search':
        param = list(map(bottle.request.query.get, 
            ['u_id', 'beginDate', 'endDate']))
        if not any(param):
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        
        db = Database(app.config)
        trans = db.get_hotel_transaction_history(param[0], param[1], param[2])

        return { 'status': 'succeeded', 'hotelTransaction': trans }
    return {'status': 'failed'}

@bottle_app.get('/manage/hotel/comment')
@bottle.view(app.config.template_path + 'manage/hotel/comment.html')
@Misc.auth_validate
def manage_hotel_comment():
    return {}

@bottle_app.get('/manage/hotel/comment/async')
@Misc.auth_validate
def hotel_comment_manage_json():
    schema = ['c_id', 'h_id', 'u_id', 'message', 'rate']
    access_type = bottle.request.query.get('type')
    if access_type == 'add':
        param = list(map(bottle.request.query.get, schema))
        if not any(param):
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success, pkey = db.add_item('hotelComment', schema, param, [0], fillpkey_autoinc)
        if success:
            return {'status': 'succeeded', 'c_id': pkey[0]}
    elif access_type == 'update':
        param = list(map(bottle.request.query.get, schema))
        if not param[0]:
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success = db.update_item('hotelComment', schema, param, [0])
        if success:
            return {'status': 'succeeded'}
    elif access_type == 'delete':
        param = list(map(bottle.request.query.get, ['c_id']))
        if not param[0]:
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        success = db.delete_item('hotelComment', schema, param, [0])
        if success:
            return {'status': 'succeeded'}
    elif access_type == 'search':
        param = list(map(bottle.request.query.get, ['u_id', 'beginDate', 'endDate']))
        if not any(param):
            return {'status': 'failed'}
        param = list(map(lambda x: Misc.unicodify(x, 'utf8'), param))
        db = Database(app.config)
        cmt = db.get_user_hotel_comment(param[0], param[1], param[2])
        return {'status': 'succeeded', 'hotelComment': cmt }
         
    return {'status': 'failed'}


if __name__ == '__main__':
    bottle.run(bottle_app, host='0.0.0.0', port=8080, debug=True)
    #bottle.run(bottle_app, server='cherrypy', host='localhost', port=8080, debug=True)

