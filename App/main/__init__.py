from flask import Blueprint
from flask_login import current_user

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

@main.app_context_processor
def inject_notifications():
    if current_user.is_authenticated:
        count = current_user.notifications.filter_by(read=False).count()
    else:
        count = 0
    return dict(unread_notification_count=count)