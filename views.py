import time

from flask import render_template, request

from core import app
from models import Website, Searches, db
from utilities import process_html
import requests
from bs4 import BeautifulSoup
import logging


@app.route('/crawl-history')
def crawl_history():
    page = request.args.get('page', default=1, type=int)
    sites = Website.query.order_by(Website.created.desc()).filter_by(newest=True)\
        .paginate(page=page, per_page=6)
    return render_template('crawl-history.html', sites=sites.items, crawls=sites)


@app.route('/search-history')
def search_history():
    page = request.args.get('page', default=1, type=int)
    searches = Searches.query.order_by(Searches.created.desc()).paginate(page=page, per_page=6)
    return render_template('search-history.html', items=searches.items, searches=searches)


@app.route('/crawl-history/<int:website_id>')
def web_history(website_id):
    new_site: Website = Website.query.get_or_404(website_id)
    old_sites = Website.query.order_by(Website.created.desc()).filter_by(url=new_site.url).all()
    return render_template('site-history.html', sites=old_sites, title=new_site.title, url=new_site.url)


@app.route('/article/<int:article_id>')
def article(article_id):
    art: Website = Website.query.get_or_404(article_id)
    return render_template('article.html', site=art)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    param = request.args.get('text')

    new_search = Searches(text=param)
    db.session.add(new_search)
    db.session.commit()

    start_time = time.time()
    sites = Website.query.msearch(param, fields=['content']).filter(Website.newest == True).all()  # noqa
    end_time = time.time()
    timer = round(end_time - start_time, 2)

    return render_template('search.html', sites=sites, time=timer, findings=len(sites), searched=param)


@app.route('/crawl')
def crawl():
    param = request.args.get('text')
    r = requests.get(param)

    # Log processing
    logging.info('Processing website: {}'.format(param))

    # Process HTML
    urls, title, text = process_html(r.content, param)

    # Disable old entry from search
    old_entry: Website = Website.query.filter_by(newest=True).first()
    if old_entry:
        old_entry.newest = False
        db.session.commit()

    # Save to DB
    new_website = Website(title=title, content=text, url=param, processed=True)
    db.session.add(new_website)
    db.session.commit()

    return render_template('index.html', scrapped_flag=True)
