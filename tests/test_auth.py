import unittest
from db import app, db
from models.user import User

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_register(self):
        response = self.app.post('/auth/register', data={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)

    def test_login(self):
        user = User(email='test@example.com', username='testuser')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        response = self.app.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)