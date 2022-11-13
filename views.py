from flask import Blueprint, render_template, request, flash, jsonify

from models import Record_data
from __init__ import db
import json


views = Blueprint('views', __name__)
