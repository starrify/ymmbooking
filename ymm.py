# This is part of coursework of Software Engineering, 2013.02-2013.07
# Source code by Pengyu CHEN (cpy.prefers.you[at]gmail.com)
# COPYLEFT, ALL WRONGS RESERVED

import bottle
from config_parser import config

class App():
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
    def index():
        return {}

    @app.get('/flight/oneway')
    @bottle.view(config.template_path + 'flight/oneway.tpl')
    @auth_validate
    def oneway_get():
        return {'flights': [
            ['Airport 1', 'Airport 2', 'Datetime 1', 'Datetime 2', 'FlighNo'], 
            ['Airport 1', 'Airport 2', 'Datetime 1', 'Datetime 2', 'FlighNo'], 
        ]}

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

