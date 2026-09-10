import unittest
from base64 import b64encode
from App import create_app, db
from App.models import User, Role, Post, Comment, Notification


class NotificationsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

        role = Role.query.filter_by(name='User').first()
        self.user_a = User(email='a@example.com', username='usera',
                           password='cat', confirmed=True, role=role)
        self.user_b = User(email='b@example.com', username='userb',
                           password='dog', confirmed=True, role=role)
        db.session.add_all([self.user_a, self.user_b])
        db.session.commit()

        self.post = Post(body='a post', author=self.user_a)
        db.session.add(self.post)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post('/auth/login', data={
            'email': email, 'password': password
        }, follow_redirects=True)

    def test_comment_on_others_post_creates_notification(self):
        comment = Comment(body='nice post', post=self.post, author=self.user_b)
        db.session.add(comment)
        db.session.flush()
        Notification.create_for_comment(comment)
        db.session.commit()

        n = Notification.query.filter_by(post_id=self.post.id).first()
        self.assertIsNotNone(n)
        self.assertEqual(n.recipient_id, self.user_a.id)
        self.assertEqual(n.actor_id, self.user_b.id)
        self.assertEqual(n.verb, 'commented')
        self.assertEqual(n.comment_id, comment.id)
        self.assertFalse(n.read)

    def test_self_comment_creates_no_notification(self):
        comment = Comment(body='my own comment', post=self.post, author=self.user_a)
        db.session.add(comment)
        db.session.flush()
        result = Notification.create_for_comment(comment)
        db.session.commit()

        self.assertIsNone(result)
        self.assertEqual(Notification.query.filter_by(post_id=self.post.id).count(), 0)

    def test_web_comment_notifies_and_marking_read(self):
        self.login('b@example.com', 'dog')
        response = self.client.post('/post/{}'.format(self.post.id),
                                    data={'body': 'a web comment'},
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.client.get('/auth/logout', follow_redirects=True)

        self.login('a@example.com', 'cat')
        self.assertEqual(self.user_a.notifications.filter_by(read=False).count(), 1)

        response = self.client.get('/notifications')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'userb', response.data)
        self.assertEqual(self.user_a.notifications.filter_by(read=False).count(), 0)

    def test_api_comment_creates_notification(self):
        headers = {
            'Authorization': 'Basic ' + b64encode(
                b'b@example.com:dog').decode('utf-8'),
            'Content-Type': 'application/json'
        }
        response = self.client.post(
            '/api/v1/posts/{}/comments/'.format(self.post.id),
            headers=headers, data='{"body": "api comment"}')
        self.assertEqual(response.status_code, 201)

        n = Notification.query.filter_by(post_id=self.post.id,
                                         actor_id=self.user_b.id).first()
        self.assertIsNotNone(n)
