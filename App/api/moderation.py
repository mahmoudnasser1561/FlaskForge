import hashlib

from flask import Blueprint, jsonify, request

from ..models import Comment, Post
from .moderation_auth import moderation_auth_required

moderation_api = Blueprint('moderation_api', __name__)


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


@moderation_api.route('/posts/<int:id>/verify', methods=['POST'])
@moderation_auth_required
def verify_post(id):
    return _verify('post', id)


@moderation_api.route('/comments/<int:id>/verify', methods=['POST'])
@moderation_auth_required
def verify_comment(id):
    return _verify('comment', id)
