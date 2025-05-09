# models/news.py
from db import db
from sqlalchemy.sql import text
from datetime import datetime

class News(db.Model):
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(100), nullable=True)  # 언론사
    thumbnail = db.Column(db.String(500), nullable=True)  # 썸네일 이미지 URL
    source_url = db.Column(db.String(500), nullable=True)  # 원본 뉴스 URL
    created_at = db.Column(db.DateTime, server_default=text("CURRENT_TIMESTAMP"))
    published_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(50), nullable=False)  # 뉴스 카테고리
    views = db.Column(db.Integer, default=0)  # 조회수
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    images = db.Column(db.JSON, nullable=True)  # 이미지 정보 JSON
    author = db.Column(db.String(100), nullable=True)  # 기사 작성자
    author_email = db.Column(db.String(150), nullable=True)  # 작성자 이메일
    
    def __repr__(self):
        return f"<News {self.id}: {self.title} - Category: {self.category}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "source": self.source,
            "thumbnail": self.thumbnail,
            "source_url": self.source_url,
            "created_at": self.created_at,
            "published_at": self.published_at,
            "category": self.category,
            "views": self.views,
            "user_id": self.user_id,
            "images": self.images,
            "author": self.author,
            "author_email": self.author_email
        }