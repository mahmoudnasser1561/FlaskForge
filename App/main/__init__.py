from flask import Blueprint
from flask_login import current_user

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission, Notification

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

@main.app_context_processor
def inject_notifications():
    if current_user.is_authenticated:
        count = current_user.notifications.filter_by(read=False).count()
        recent = current_user.notifications.order_by(
            Notification.timestamp.desc()).limit(5).all()
    else:
        count = 0
        recent = []
    return dict(unread_notification_count=count, recent_notifications=recent)