from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from db import db  # db 객체를 db.py에서 가져옴

db = SQLAlchemy()

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, nullable=False)  # 로그인 성공 여부

    def __repr__(self):
        return f"<LoginAttempt user_id={self.user_id} success={self.success}>"
