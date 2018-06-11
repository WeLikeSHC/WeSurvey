# coding = utf-8

import ConfigParser

cf = ConfigParser.ConfigParser()


class ServerConfig(object):
    SECRET_KEY = "hard to guess string"
    cf.read("./system.ini")
    OWNER = cf.get("owner", "owner")
    DATABASE = cf.get("database", "database")
    PORT = cf.get("port", "port")
    LISTEN_PORT = cf.get("ServerConfig", "server_listen_port")
    PASSWORD = cf.get('password', 'password')
    HOST = cf.get('host', 'host')
    RPC_ADDRESS = cf.get('rpc_address', 'rpc_address')
    UI_ADDRESS = cf.get('ui_address', 'ui_address')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'mysql://' + OWNER + ':' + PASSWORD + '@' + \
                              HOST + ':' + PORT + "/" + DATABASE

    @staticmethod
    def init_app(app):
        pass


config = {
    "default": ServerConfig
}
