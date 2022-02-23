from flask import Blueprint

view = Blueprint('view', __name__)

from . import auth, flats, societies, users, collections, transactions