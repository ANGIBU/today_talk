import unittest
from db import app, db
from models.user import User
from models.post import Post
from models.comment import Comment
from flask_login import login_user

class TestComments(unittest.TestCase):
    def setUp(self):
        """
        테스트 환경 초기화
        """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # 테스트용 SQLite
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

            # 테스트 사용자 및 게시글 생성
            self.user = User(username='testuser', email='testuser@example.com', password='testpassword')
            db.session.add(self.user)
            db.session.commit()

            self.post = Post(title='Test Post', content='Test Content', user_id=self.user.id)
            db.session.add(self.post)
            db.session.commit()

    def tearDown(self):
        """
        테스트 종료 후 데이터베이스 정리
        """
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_comment(self):
        """
        댓글 생성 테스트
        """
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = self.user.id  # 로그인 상태 시뮬레이션
            
            response = client.post(f'/comments/{self.post.id}/create', data={
                'content': 'Test Comment'
            })
            self.assertEqual(response.status_code, 302)  # 리다이렉트 확인
            with app.app_context():
                comment = Comment.query.filter_by(content='Test Comment').first()
                self.assertIsNotNone(comment)

    def test_edit_comment(self):
        """
        댓글 수정 테스트
        """
        with app.app_context():
            comment = Comment(content='Original Comment', post_id=self.post.id, user_id=self.user.id)
            db.session.add(comment)
            db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = self.user.id  # 로그인 상태 시뮬레이션

            response = client.post(f'/comments/{comment.id}/edit', data={
                'content': 'Updated Comment'
            })
            self.assertEqual(response.status_code, 302)
            with app.app_context():
                updated_comment = Comment.query.get(comment.id)
                self.assertEqual(updated_comment.content, 'Updated Comment')

    def test_delete_comment(self):
        """
        댓글 삭제 테스트
        """
        with app.app_context():
            comment = Comment(content='To Be Deleted', post_id=self.post.id, user_id=self.user.id)
            db.session.add(comment)
            db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = self.user.id  # 로그인 상태 시뮬레이션

            response = client.post(f'/comments/{comment.id}/delete')
            self.assertEqual(response.status_code, 302)
            with app.app_context():
                deleted_comment = Comment.query.get(comment.id)
                self.assertIsNone(deleted_comment)