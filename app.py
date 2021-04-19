#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import re
import time
import scrapper

from flask import Flask, render_template, request
from flask_msearch import Search
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

search = Search()
search.init_app(app)


class Website(db.Model):
    __searchable__ = ['content']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.String(50000))  # 50 kB
    url = db.Column(db.String(255))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)


@app.template_filter()
def begin(text):
    """Convert a string to all caps."""
    param = request.args.get('text')
    matching = re.search(param, text, re.IGNORECASE).span()
    start = matching[0] - 150
    return text[start:matching[0]]


@app.template_filter()
def end(text):
    """Convert a string to all caps."""
    param = request.args.get('text')
    matching = re.search(param, text, re.IGNORECASE).span()
    ending = matching[1] + 150
    return text[matching[1]:ending]


@app.template_filter()
def match(text):
    """Convert a string to all caps."""
    param = request.args.get('text')
    matching = re.search(param, text, re.IGNORECASE).span()
    return text[matching[0]:matching[1]]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    param = request.args.get('text')

    start_time = time.time()
    sites = Website.query.msearch(param, fields=['content']).all()
    end_time = time.time()

    return render_template('search.html',
                           sites=sites,
                           time=round(end_time - start_time, 2),
                           findings=len(sites),
                           searched=param)


@app.route('/crawl')
def crawl():
    param = request.args.get('text')

    start_time = time.time()
    scrapper.crawl(param)
    end_time = time.time()

    return render_template('index.html',
                           scrapped_flag=True)


if __name__ == '__main__':
    # Run Application
    app.run(debug=True)
