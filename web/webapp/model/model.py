# coding=utf-8

from web.webapp import db
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime


class Sensor(db.Model):
    __tablename__ = 'information'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    type = db.Column(db.String(50), unique=True)
    entry_time = db.Column(db.DateTime, nullable=False)
    entry_data = db.Column(db.Text(1000), nullable=False)
    info = db.Column(db.Text(1000))
    # sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable=False)


# class Sensor(db.Model):
#     __tablename__ = 'sensor'
#
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64), unique=True)
#     type = db.Column(db.String(50), unique=True)
#     info = db.Column(db.String(100))
#     entry_time = db.Column(db.DateTime, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     infoes = db.relationship('information', foreign_keys=[Information.id],
#                              backref=db.backref('infoes', lazy='joined'), lazy='dynamic',
#                              cascade='all, delete-orphan')
#
#
# class User(db.Model, UserMixin):
#     __tablename__ = 'user'
#
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64), unique=True)
#     password = db.Column(db.String(20), nullable=False)
#     last_login = entry_time = db.Column(db.DateTime, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#     sensors = db.relationship('sensor', foreign_keys=[Sensor.id],
#                               backref=db.backref('sensors', lazy='joined'), lazy='dynamic',
#                               cascade='all, delete-orphan')
