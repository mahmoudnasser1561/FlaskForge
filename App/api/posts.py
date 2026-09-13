from datetime import datetime
from flask import jsonify, request, g, url_for, current_app
from .. import db, cache
from ..models import Post, Permission, ModerationFlag
from . import api
from .decorators import permission_required
from .errors import forbidden
from ..moderation import queue_for_moderation


@api.route('/posts/')
@cache.cached(timeout=60, query_string=True)
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page=page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/posts/<int:id>')
@cache.cached(timeout=60)
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    queue_for_moderation('post', post)
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id, _external=True)}


@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author:
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())


@api.route('/posts/<int:id>/disable', methods=['POST'])
@permission_required(Permission.MODERATE)
def disable_post(id):
    post = Post.query.get_or_404(id)
    if not post.disabled:
        post.disabled = True
        db.session.add(post)
        flag = ModerationFlag(source='admin', reason=None,
                              moderator_id=g.current_user.id,
                              user_id=post.author_id,
                              post_id=post.id, comment_id=None)
        db.session.add(flag)
        db.session.commit()
    return jsonify(post.to_json())


@api.route('/posts/<int:id>/enable', methods=['POST'])
@permission_required(Permission.MODERATE)
def enable_post(id):
    post = Post.query.get_or_404(id)
    if post.disabled:
        post.disabled = False
        db.session.add(post)
        flag = ModerationFlag.query.filter_by(
            post_id=post.id, comment_id=None, overturned_at=None).order_by(
            ModerationFlag.timestamp.desc()).first()
        if flag is not None:
            flag.overturned_at = datetime.utcnow()
            flag.overturned_by_id = g.current_user.id
            db.session.add(flag)
        db.session.commit()
    return jsonify(post.to_json())
