import unittest
from services.user_service import register_user, authenticate_user, check_duplicate
from models.user import User
from db import db

class TestUserService(unittest.TestCase):

    def setUp(self):
        """테스트 환경 설정"""
        # 테스트용 데이터베이스 초기화
        self.app = db.app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """테스트 환경 정리"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_user_success(self):
        """사용자 등록 성공 테스트"""
        result, message = register_user("test@example.com", "testuser", "password123", "testnickname")
        self.assertTrue(result)
        self.assertEqual(message, "회원가입 성공!")

    def test_register_user_existing_email(self):
        """이미 존재하는 이메일로 사용자 등록 테스트"""
        register_user("test@example.com", "testuser", "password123", "testnickname")
        result, message = register_user("test@example.com", "anotheruser", "password456", "anothernickname")
        self.assertFalse(result)
        self.assertEqual(message, "이미 등록된 이메일입니다.")

    def test_register_user_existing_username(self):
        """이미 존재하는 아이디로 사용자 등록 테스트"""
        register_user("test@example.com", "testuser", "password123", "testnickname")
        result, message = register_user("another@example.com", "testuser", "password456", "anothernickname")
        self.assertFalse(result)
        self.assertEqual(message, "이미 등록된 아이디입니다.")

    def test_register_user_existing_nickname(self):
        """이미 존재하는 닉네임으로 사용자 등록 테스트"""
        register_user("test@example.com", "testuser", "password123", "testnickname")
        result, message = register_user("another@example.com", "anotheruser", "password456", "testnickname")
        self.assertFalse(result)
        self.assertEqual(message, "이미 사용 중인 닉네임입니다.")

    def test_authenticate_user_success(self):
        """사용자 인증 성공 테스트"""
        register_user("test@example.com", "testuser", "password123", "testnickname")
        user = authenticate_user("testuser", "password123")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")

    def test_authenticate_user_failure(self):
        """잘못된 인증 정보로 인증 실패 테스트"""
        register_user("test@example.com", "testuser", "password123", "testnickname")
        user = authenticate_user("testuser", "wrongpassword")
        self.assertIsNone(user)

    def test_check_duplicate_email(self):
        """이메일 중복 확인 테스트"""
        register_user("test@example.com", "testuser", "password123", "testnickname")
        is_duplicate = check_duplicate("email", "test@example.com")
        self.assertTrue(is_duplicate)

    def test_check_duplicate_username(self):
        """아이디 중복 확인 테스트"""
        register_user("test@example.com", "testuser", "password123", "testnickname")
        is_duplicate = check_duplicate("username", "testuser")
        self.assertTrue(is_duplicate)

    def test_check_duplicate_nickname(self):
        """닉네임 중복 확인 테스트"""
        register_user("test@example.com", "testuser", "password123", "testnickname")
        is_duplicate = check_duplicate("nickname", "testnickname")
        self.assertTrue(is_duplicate)

if __name__ == "__main__":
    unittest.main()
