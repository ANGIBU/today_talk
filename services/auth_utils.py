from flask_login import current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from db import db

# 사용자 등록 함수
def register_user(email, username, password, nickname):
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return False, '이미 존재하는 사용자 이름 또는 이메일입니다.'

    try:
        new_user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password),
            nickname=nickname
        )
        db.session.add(new_user)
        db.session.commit()
        return True, '회원가입 성공'
    except Exception as e:
        db.session.rollback()
        return False, f'회원가입 실패: {str(e)}'

# 사용자 인증 함수
def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None

# 비밀번호 재설정 이메일 전송 함수
def send_reset_email(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return False
    # 여기에 이메일 전송 로직 추가 (예: Flask-Mail 사용)
    return True

# 중복 확인 함수
def check_duplicate(field, value):
    if field not in ['username', 'email', 'nickname']:
        raise ValueError('허용되지 않은 필드입니다.')

    filter_condition = {field: value}
    exists = User.query.filter_by(**filter_condition).first() is not None
    return exists
