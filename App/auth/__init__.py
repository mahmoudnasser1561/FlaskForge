from flask import Blueprint
from .. import db, limiter

auth = Blueprint('auth', __name__)

from . import views 
