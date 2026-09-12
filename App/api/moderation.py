import hashlib

from flask import Blueprint, current_app, jsonify, request

from .. import db
from ..email import send_email
from ..models import Comment, ModerationFlag, Post
from .moderation_auth import moderation_auth_required

moderation_api = Blueprint('moderation_api', __name__)

REASON_MAX_LENGTH = 500


def _load_content(kind, id):
    if kind == 'post':
        return Post.query.get(id)
    return Comment.query.get(id)


def _current_hash(row):
    return hashlib.sha256(row.body.encode('utf-8')).hexdigest()


def _verify(kind, id):
    row = _load_content(kind, id)
    if row is None:
        return jsonify(status='not_found'), 404
    content_hash = (request.get_json(silent=True) or {}).get('content_hash')
    if content_hash != _current_hash(row):
        return jsonify(status='stale')
    return jsonify(status='ok')


def _disable(kind, id):
    row = _load_content(kind, id)
    if row is None:
        return jsonify(status='not_found'), 404

    body = request.get_json(silent=True) or {}
    content_hash = body.get('content_hash')
    if content_hash != _current_hash(row):
        return jsonify(status='stale_skipped')

    if row.disabled:
        return jsonify(status='already_disabled')

    reason = (body.get('reason') or '').strip()
    if not reason:
        response = jsonify(error='bad request',
                           message='reason must be a non-empty string')
        return response, 400
    reason = reason[:REASON_MAX_LENGTH]

    row.disabled = True
    db.session.add(row)

    if kind == 'post':
        flag = ModerationFlag(source='ai', reason=reason, user_id=row.author_id,
                              post_id=row.id, comment_id=None)
        template = 'moderation/email/post_disabled'
        template_kwargs = {'post': row, 'reason': reason}
    else:
        flag = ModerationFlag(source='ai', reason=reason, user_id=row.author_id,
                              post_id=row.post_id, comment_id=row.id)
        template = 'moderation/email/comment_disabled'
        template_kwargs = {'comment': row, 'reason': reason}

    db.session.add(flag)
    db.session.commit()

    send_email(current_app.config['FLASKY_ADMIN'], 'AI Moderation Alert',
              template, **template_kwargs)

    return jsonify(status='disabled', id=row.id, type=kind)


@moderation_api.route('/posts/<int:id>/verify', methods=['POST'])
@moderation_auth_required
def verify_post(id):
    return _verify('post', id)


@moderation_api.route('/comments/<int:id>/verify', methods=['POST'])
@moderation_auth_required
def verify_comment(id):
    return _verify('comment', id)


@moderation_api.route('/posts/<int:id>/disable', methods=['POST'])
@moderation_auth_required
def disable_post(id):
    return _disable('post', id)


@moderation_api.route('/comments/<int:id>/disable', methods=['POST'])
@moderation_auth_required
def disable_comment(id):
    return _disable('comment', id)
