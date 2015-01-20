from flask import Blueprint

api = Blueprint('api', __name__)

from . import alarm
from . import dsn
