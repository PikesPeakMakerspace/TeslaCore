# deliver static production React build

from .app import app
from flask import Blueprint
from flask import send_from_directory, send_file

ui = Blueprint('ui', __name__)


# index
@app.route('/')
def react_ui_index():
    return send_file('../ui/build/index.html')


# favicon, manifest, etc.
@app.route('/<path:name>')
def react_ui_root(name):
    return send_from_directory('../ui/build', name)


# css
@app.route('/static/css/<path:name>')
def react_ui_css(name):
    return send_from_directory('../ui/build/static/css', name)


# js
@app.route('/static/js/<path:name>')
def react_ui_js(name):
    return send_from_directory('../ui/build/static/js', name)


# media
@app.route('/static/media/<path:name>')
def react_ui_media(name):
    return send_from_directory('../ui/build/static/media', name)
