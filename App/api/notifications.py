from flask import jsonify, request, g, current_app, url_for
from . import api
from .. import db
from ..models import Notification


@api.route('/notifications/')
def get_notifications():
    page = request.args.get('page', 1, type=int)
    pagination = g.current_user.notifications.order_by(
        Notification.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['FLASKY_NOTIFICATIONS_PER_PAGE'],
        error_out=False)
    items = pagination.items
    unread_ids = [n.id for n in items if not n.read]
    if unread_ids:
        Notification.query.filter(Notification.id.in_(unread_ids)).update(
            {'read': True}, synchronize_session=False)
        db.session.commit()
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_notifications', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_notifications', page=page+1)
    return jsonify({
        'notifications': [n.to_json() for n in items],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
