from datetime import datetime
from sqlalchemy import text
from db import db  # ✅ db.py에서 db 객체를 가져옴

class News(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(100), nullable=True)  # ✅ 언론사 필드 추가
    thumbnail = db.Column(db.String(500), nullable=True)  # ✅ 썸네일 필드 추가
    source_url = db.Column(db.String(500), nullable=True)  # ✅ 뉴스 원본 URL
    created_at = db.Column(db.DateTime, server_default=text("CURRENT_TIMESTAMP"))  # DB에서 기본값 설정
    published_at = db.Column(db.DateTime, nullable=False)  # 뉴스가 실제로 발행된 날짜
    category = db.Column(db.String(50), nullable=False)  # 뉴스 카테고리
    views = db.Column(db.Integer, default=0)  # ✅ 조회수 필드 추가
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<News {self.title}>"
