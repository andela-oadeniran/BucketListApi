#!/usr/bin/env python
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    BASE_DIR + 'buckelist.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ERROR_404_HELP'] = False
db = SQLAlchemy(app)
