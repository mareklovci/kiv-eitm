import datetime

from flask_msearch import Search
from flask_sqlalchemy import SQLAlchemy

from core import app

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
    processed = db.Column(db.Boolean, default=False)
    level = db.Column(db.Integer, default=0)


def main():
    db.drop_all()
    db.create_all()


if __name__ == '__main__':
    main()
