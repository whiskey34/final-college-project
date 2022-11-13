from flask_sqlalchemy import SQLAlchemy
from flask import Flask, session, url_for, render_template
import flask_login as FL
from flask_login import LoginManager
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'recogweb1223'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///recogweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
