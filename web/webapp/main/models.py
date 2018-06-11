# coding=utf-8

from flask_login import UserMixin, AnonymousUserMixin
from .. import db, login_manager, online


class Sensor(db.Model):
    __tablename__ = 'sensor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    type = db.Column(db.String(50), unique=True)
    entry_time = db.Column(db.DateTime, nullable=False)
    entry_data = db.Column(db.Text(1000), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    info = db.Column(db.Text(1000))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)

    email = db.Column(db.String(64), unique=True, index=True)  # 添加索引

    image_name = db.Column(db.String(20), unique=True)

    username = db.Column(db.String(20), nullable=False, unique=True)

    about_me = db.Column(db.String(100), default="")


class AnonymousUser(AnonymousUserMixin):
    role_id = 3

    @staticmethod
    def can():
        return False

    @staticmethod
    def is_administrator():
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return online.get(int(user_id))
