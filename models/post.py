# models/post.py
from db import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Post(db.Model):
    __tablename__ = "posts"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    likes = db.Column(db.Integer, default=0, nullable=False)
    views = db.Column(db.Integer, default=0, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    images = db.Column(db.JSON, nullable=True)  # 이미지 파일명 목록 저장
    
    # 관계 설정
    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Post {self.id}: {self.title} - Category: {self.category}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id,
            "likes": self.likes,
            "views": self.views,
            "category": self.category,
            "images": self.images,
            "comment_count": len(self.comments) if self.comments else 0,
            "author": self.user.username if self.user else None
        }