## security.py
# 보안 관련 유틸리티
import hashlib
import hmac

def hash_password(password, salt):
    """비밀번호를 해시로 변환"""
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

def verify_password(password, salt, hashed):
    """비밀번호 검증"""
    return hmac.compare_digest(hash_password(password, salt), hashed)