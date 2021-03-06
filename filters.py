import re

from flask import request

from core import app
from babel.dates import format_datetime as fdt


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


@app.template_filter()
def format_datetime(value):
    form = "HH:mm, dd.MM.yyyy"
    return fdt(value, form)
