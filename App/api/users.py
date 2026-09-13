from flask import jsonify, request, g, current_app, url_for
from . import api
from .. import db, cache
from ..models import User, Post
from .errors import bad_request


@api.route('/users/<int:id>')
@cache.cached(timeout=60)
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_posts', id=id, page=page+1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/users/me', methods=['PUT'])
def edit_user():
    name = request.json.get('name', g.current_user.name)
    location = request.json.get('location', g.current_user.location)
    if name and len(name) > 64:
        return bad_request('name must be 64 characters or fewer')
    if location and len(location) > 64:
        return bad_request('location must be 64 characters or fewer')
    g.current_user.name = name
    g.current_user.location = location
    g.current_user.about_me = request.json.get('about_me', g.current_user.about_me)
    db.session.add(g.current_user)
    db.session.commit()
    return jsonify(g.current_user.to_json())


@api.route('/users/<int:id>/timeline/')
def get_user_followed_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_followed_posts', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_followed_posts', id=id, page=page+1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
