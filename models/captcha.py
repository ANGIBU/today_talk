from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from db import db  # db 객체를 db.py에서 가져옴

db = SQLAlchemy()

class Captcha(db.Model):
    __tablename__ = 'captchas'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(6), nullable=False)  # 예: 6자리 캡차
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # 추가적으로, 사용자의 아이디와 연결할 수 있도록 외래키를 추가할 수 있음
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __repr__(self):
        return f"<Captcha {self.text}>"
