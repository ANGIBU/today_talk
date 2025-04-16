# user_service.py
from db import db
from models.user import User

# 중복 확인 함수
def check_duplicate(field, value):
    """Check for duplicate user fields (e.g., username, email)"""
    if field not in ['username', 'email', 'nickname']:
        raise ValueError('Invalid field for duplicate check.')
    filter_condition = {field: value}
    exists = User.query.filter_by(**filter_condition).first() is not None
    return exists

class UserService:
    @staticmethod
    def register_user(username, password, email):
        """Register a new user"""
        if not username or not password or not email:
            return "All fields are required."
        # 사용자 등록 코드 (예: 데이터베이스 저장)
        return f"User {username} has been registered successfully!"

    @staticmethod
    def login_user(username, password):
        """Login user with username and password"""
        if not username or not password:
            return "Username and password are required."
        # 로그인 검증 코드 추가
        return f"User {username} has logged in successfully!"

    @staticmethod
    def update_profile(user_id, new_data):
        """Update user profile"""
        if not user_id or not new_data:
            return "User ID and new data are required."
        # 프로필 업데이트 코드 추가
        return f"User profile for {user_id} has been updated successfully!"
