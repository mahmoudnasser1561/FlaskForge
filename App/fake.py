from random import choice
from faker import Faker
from . import db
from .models import User, Post
from sqlalchemy.exc import IntegrityError
fake = Faker()

def create_users(count=100):
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
            i += 1
        except IntegrityError:
            db.session.rollback()

def create_posts(count=100):
    users_list = User.query.all()
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
