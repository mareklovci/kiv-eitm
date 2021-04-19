import time

from flask import render_template, request

from core import app
from models import Website, db
from utilities import process_html
import requests
from bs4 import BeautifulSoup
import logging


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


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
    r = requests.get(param)

    # Log processing
    logging.info('Processing website: {}'.format(param))

    # Process HTML
    urls, title, text = process_html(r.content, param)

    # Save to DB
    new_website = Website(title=title, content=text, url=param, processed=True)
    db.session.add(new_website)
    db.session.commit()

    return render_template('index.html', scrapped_flag=True)
