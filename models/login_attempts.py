# models/login_attempts.py
from datetime import datetime
from db import db

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 로그인 시도한 사용자 ID
    ip_address = db.Column(db.String(50), nullable=False)  # 접속 IP 주소
    username = db.Column(db.String(150), nullable=True)  # 로그인 시도한 사용자명
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, nullable=False)  # 로그인 성공 여부
    user_agent = db.Column(db.String(255), nullable=True)  # 접속 기기 정보
    
    def __repr__(self):
        return f"<LoginAttempt id={self.id} user_id={self.user_id} success={self.success}>"
        
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "username": self.username,
            "timestamp": self.timestamp,
            "success": self.success,
            "user_agent": self.user_agent
        }