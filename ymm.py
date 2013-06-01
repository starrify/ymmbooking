# This is part of coursework of Software Engineering, 2013.02-2013.07
# Source code by Pengyu CHEN (cpy.prefers.you[at]gmail.com)
# COPYLEFT, ALL WRONGS RESERVED

import bottle
from config_parser import config

app = bottle.Bottle()

@app.route('/')
def index():
    return "well here i'm just a testing message"

@app.route('/view/<filepath:path>')
def view(filepath):   
    return bottle.static_file(filepath, root=config.view_path)

bottle.run(app, host='localhost', port=8080, debug=True)

