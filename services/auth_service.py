# services/auth_service.py
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.login_attempts import LoginAttempt
from db import db
from datetime import datetime

def register_user(email, username, password, nickname):
    """
    새로운 사용자 등록
    """
    # 이메일 중복 확인
    if User.query.filter_by(email=email).first():
        return False, "이미 등록된 이메일입니다."
    
    # 아이디 중복 확인
    if User.query.filter_by(username=username).first():
        return False, "이미 등록된 아이디입니다."
    
    # 닉네임 중복 확인
    if nickname and User.query.filter_by(nickname=nickname).first():
        return False, "이미 사용 중인 닉네임입니다."
    
    try:
        # 새 사용자 생성
        new_user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password),
            nickname=nickname or username  # 닉네임이 없으면 아이디를 닉네임으로 사용
        )
        
        db.session.add(new_user)
        db.session.commit()
        return True, "회원가입 성공!"
    except Exception as e:
        db.session.rollback()
        return False, f"회원가입 실패: {str(e)}"

def authenticate_user(username, password, ip_address=None, user_agent=None):
    """
    사용자 인증
    """
    user = User.query.filter_by(username=username).first()
    success = False
    
    if user and check_password_hash(user.password_hash, password):
        success = True
        
    # 로그인 시도 기록
    if ip_address:
        login_attempt = LoginAttempt(
            user_id=user.id if user else None,
            username=username,
            ip_address=ip_address,
            success=success,
            user_agent=user_agent
        )
        db.session.add(login_attempt)
        db.session.commit()
        
    return user if success else None

def check_duplicate(field, value):
    """
    중복 확인 (아이디, 이메일, 닉네임)
    """
    if field not in ['username', 'email', 'nickname']:
        raise ValueError('허용되지 않은 필드입니다.')
    
    # 필드별 중복 확인
    filter_condition = {field: value}
    exists = User.query.filter_by(**filter_condition).first() is not None
    return exists

def send_reset_email(email):
    """
    비밀번호 재설정 이메일 전송
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        return False
    
    # 비밀번호 재설정 토큰 생성 및 이메일 전송 로직
    # (실제 이메일 전송 로직은 구현 필요)
    
    return True

def reset_password(user_id, new_password):
    """
    비밀번호 재설정
    """
    user = User.query.get(user_id)
    if not user:
        return False, "사용자를 찾을 수 없습니다."
    
    try:
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return True, "비밀번호가 성공적으로 변경되었습니다."
    except Exception as e:
        db.session.rollback()
        return False, f"비밀번호 변경 실패: {str(e)}"