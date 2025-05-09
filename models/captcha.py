# models/captcha.py
from datetime import datetime
from db import db

class Captcha(db.Model):
    __tablename__ = 'captchas'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(6), nullable=False)  # CAPTCHA 텍스트
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)  # 만료 시간
    is_used = db.Column(db.Boolean, default=False)  # 사용 여부
    session_id = db.Column(db.String(100), nullable=False)  # 세션 ID
    
    def __repr__(self):
        return f"<Captcha {self.id}: {self.text}>"
        
    def is_expired(self):
        """CAPTCHA 만료 여부 확인"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "is_used": self.is_used,
            "session_id": self.session_id
        }