import os

from flask import Flask

basedir = os.getcwd()

app = Flask(__name__, template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

import views
import filters
import models
