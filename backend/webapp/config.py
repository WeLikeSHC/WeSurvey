# coding=utf-8

import os
import ConfigParser


config_file = "./mysql.ini"

if not os.path.exists(config_file):
    raise Exception("config file not find!")

cf = ConfigParser.ConfigParser()
cf.read(config_file)


class Config:
    def __init__(self):
        self.listen_port = cf.get("listen_port", 'port')
        self.database = cf.get('database', 'database')
        self.owner = cf.get('owner', 'owner')
        self.password = cf.get('password', 'password')
        self.port = cf.get('port', 'port')
        self.driver = cf.get('driver', 'driver')
        self.rpc_port = cf.get('rpc_port', 'rpc_port')
        self.cp_max = cf.get('cp_max', 'cp_max')
        self. cp_min = cf.get('cp_min', 'cp_min')
        self.max_logfile = cf.get('max_logfile', 'max_logfile')
        self.host = cf.get('host', 'host')
        self.ui_port = cf.get('ui_port', 'port')
        self.slave_port = cf.get('slave_port', 'port')


config = Config()

if __name__ == '__main__':
    print config.listen_port
    print config.database
    print config.password
    print config.owner
    print config.rpc_port
    print config.cp_max
    print config.cp_min
    print config.max_logfile
    print config.host
