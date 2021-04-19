import re

from flask import request

from core import app


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
