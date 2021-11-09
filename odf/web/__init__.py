import io
import logging as log
import os
import webbrowser
from datetime import datetime
from subprocess import Popen

from flask import (Blueprint, Flask, abort, jsonify, redirect, request,
                   send_file, send_from_directory, url_for)
from odf.config import config
from flask_cors import CORS
from odf.web.rest import *

from .resources import bp_api

app = Flask(config.FLASK_NAME, static_url_path='/dist')
CORS(app)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['FLASK_DEBUG'] = 1

__dir_path = os.path.dirname(
    os.path.realpath(__file__))
__static_folder = os.path.join(
    __dir_path, 'static',
)
app.static_folder = __static_folder

app.register_blueprint(bp_api)


@app.route("/")
def serve():
    """serves React App"""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    """static folder serve"""
    file_name = path.split("/")[-1]
    dir_name = "/".join(path.split("/")[:-1])
    dir_name = os.path.join(app.static_folder, dir_name)
    if request.path.startswith("/api/dat/"):
        return send_from_directory(config.DATA_PATH, request.path[9:])
    return send_from_directory(dir_name, file_name)


@app.errorhandler(404)
def handle_404(e):
    if request.path.startswith("/api/"):
        return jsonify(err=True, message="Resource not found"), 404
    return send_from_directory(app.static_folder, "index.html")


@app.errorhandler(405)
def handle_405(e):
    if request.path.startswith("/api/"):
        return jsonify(err=True, message="Mehtod not allowed"), 405
    return e


def print_mapping(app):
    for rule in app.url_map.iter_rules():
        log.info('Web API mapping %s', rule)


print_mapping(app)


def start_integrated_server():
    app.run(host='0.0.0.0', debug=True, port=config.FLASK_PORT, threaded=True)
