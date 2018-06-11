# coding=utf-8

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager
from flask import render_template
from config import config


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.index"
online = dict()


def create_app(object_name):
    from main.auth import auth

    app = Flask(__name__)
    app.config.from_object(config[object_name])
    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(auth)

    @app.errorhandler(404)
    def page_not_find(e):
        return render_template("error/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("error/500.html"), 500

    return app


