# This is part of coursework of Software Engineering, 2013.02-2013.07
# Source code by Pengyu CHEN (cpy.prefers.you[at]gmail.com)
# COPYLEFT, ALL WRONGS RESERVED

class _config():
    def __init__(self, config_path='./config.cfg'): 
        import configparser
        parser = configparser.ConfigParser()
        parser.read(config_path)

        # the following parsings shall not fail
        self.database_path  = parser.get('Path', 'database_path')
        self.static_path    = parser.get('Path', 'static_path')
        self.view_path      = parser.get('Path', 'view_path')

config = _config()
