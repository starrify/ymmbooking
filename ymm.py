# This is part of coursework of Software Engineering, 2013.02-2013.07
# Source code by Pengyu CHEN (cpy.prefers.you[at]gmail.com)
# COPYLEFT, ALL WRONGS RESERVED

import bottle
from config_parser import config

app = bottle.Bottle()

@app.route('/')
@app.route('/index')
@bottle.view(config.template_path + 'index.tpl')
def index():
    return {}

# routes static files
@app.route('/static/<filepath:path>')
def view(filepath):   
    return bottle.static_file(filepath, root=config.static_path)

bottle.run(app, host='localhost', port=8080, debug=True)

