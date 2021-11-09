import logging as log
import os

from flask import Blueprint
from flask_restful import reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from odf.config import config

bp_api = Blueprint('api', __name__, url_prefix='/api')
bp_web = Blueprint('web', __name__, url_prefix='/web')


def configure_parser_for_file(parser: reqparse.RequestParser, name='file'):
    parser.add_argument(
        name, type=FileStorage, location='files', required=True, action='append')
