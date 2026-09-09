from random import choice, sample
from faker import Faker
from . import db
from .models import User, Post, Comment
from sqlalchemy.exc import IntegrityError
fake = Faker()

def create_users(count=100):
    users = []
    i = 0
    while i < count:
        username = fake.user_name()
        u = User(
            email=fake.email(),
            username=username,
            password='password',
            confirmed=True,
            name=fake.name(),
            location=fake.city(),
            about_me=fake.text(),
            member_since=fake.date_time_this_decade()
        )
        db.session.add(u)
        try:
            db.session.commit()
            users.append(u)
            i += 1
        except IntegrityError:
            db.session.rollback()
    return users

def create_posts(count=100, authors=None):
    users_list = authors if authors is not None else User.query.all()
    if not users_list:
        raise Exception("No users found! Create users first.")
    for _ in range(count):
        user = choice(users_list)
        post = Post(
            body=fake.text(),
            timestamp=fake.date_time_this_year(),
            author=user
        )
        db.session.add(post)
    db.session.commit()

def create_followers(users, max_per_user=8):
    if not users:
        raise Exception("No users given to create follows for.")
    for user in users:
        others = [u for u in users if u.id != user.id]
        if not others:
            continue
        for other in sample(others, min(max_per_user, len(others))):
            user.follow(other)
    db.session.commit()

def create_comments(count=100, authors=None, posts=None):
    users_list = authors if authors is not None else User.query.all()
    posts_list = posts if posts is not None else Post.query.all()
    if not users_list or not posts_list:
        raise Exception("No users or posts found! Create them first.")
    for _ in range(count):
        comment = Comment(
            body=fake.text(),
            timestamp=fake.date_time_this_year(),
            author=choice(users_list),
            post=choice(posts_list)
        )
        db.session.add(comment)
    db.session.commit()
