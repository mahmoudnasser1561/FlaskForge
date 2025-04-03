from flask import Blueprint
from .. import db

auth = Blueprint('auth', __name__)

from . import views 
