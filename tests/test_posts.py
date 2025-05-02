# tests\test_posts.py
import unittest
from app import app, db
from models.user import User
from models.post import Post
from flask_login import login_user

class TestPosts(unittest.TestCase):
    def setUp(self):
        """
        테스트 환경 초기화
        """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # 테스트용 SQLite
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

            # 테스트 사용자 생성
            self.user = User(username='testuser', email='testuser@example.com', password='testpassword')
            db.session.add(self.user)
            db.session.commit()

    def tearDown(self):
        """
        테스트 종료 후 데이터베이스 정리
        """
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_post(self):
        """
        게시글 생성 테스트
        """
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = self.user.id  # 로그인 상태 시뮬레이션
            
            response = client.post('/posts/create', data={
                'title': 'Test Post',
                'content': 'This is a test post content.'
            })
            self.assertEqual(response.status_code, 302)  # 리다이렉트 확인
            with app.app_context():
                post = Post.query.filter_by(title='Test Post').first()
                self.assertIsNotNone(post)

    def test_edit_post(self):
        """
        게시글 수정 테스트
        """
        with app.app_context():
            post = Post(title='Original Title', content='Original Content', user_id=self.user.id)
            db.session.add(post)
            db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = self.user.id  # 로그인 상태 시뮬레이션
            
            response = client.post(f'/posts/{post.id}/edit', data={
                'title': 'Updated Title',
                'content': 'Updated Content'
            })
            self.assertEqual(response.status_code, 302)
            with app.app_context():
                updated_post = Post.query.get(post.id)
                self.assertEqual(updated_post.title, 'Updated Title')

    def test_delete_post(self):
        """
        게시글 삭제 테스트
        """
        with app.app_context():
            post = Post(title='To Be Deleted', content='Content', user_id=self.user.id)
            db.session.add(post)
            db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = self.user.id  # 로그인 상태 시뮬레이션

            response = client.post(f'/posts/{post.id}/delete')
            self.assertEqual(response.status_code, 302)
            with app.app_context():
                deleted_post = Post.query.get(post.id)
                self.assertIsNone(deleted_post)