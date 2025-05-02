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
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    likes = db.Column(db.Integer, default=0, nullable=False)
    views = db.Column(db.Integer, default=0, nullable=False)
    category = db.Column(db.String(50), nullable=False)

    # User relationship
    user = relationship("User", back_populates="posts")
    # Comments relationship
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Post {self.title} - Category: {self.category} - Likes: {self.likes} - Views: {self.views}>"

    # 게시글 정보를 딕셔너리로 변환하는 메서드 추가
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
            "comment_count": len(self.comments)  # 댓글 수 추가
        }