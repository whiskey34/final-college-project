from pytz import timezone
from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import datetime

from __init__ import db, app


from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData

engine = create_engine('sqlite:///recogweb.db', echo=True)

meta = MetaData()


class Record_absen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(255))
    status = db.Column(db.String(255))
    img = db.Column(db.String(255))
    time = db.Column(db.DateTime)
    create_at = db.Column(db.DateTime(timezone=True), default=func.now())

    def __init__(self, label=None, status=None, img=None, time=None, create_at=None):
        self.label = label
        self.status = status
        self.img = img
        self.time = time
        self.create_at = create_at


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode(128))
    name = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(1024))
    authenticated = db.Column(db.Boolean, default=False)


db.create_all()

# def save(self):

#     db.session.add(self)

#     db.session.commit()

#     return self
