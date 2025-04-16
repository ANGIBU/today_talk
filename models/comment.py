from datetime import datetime
from db import db
from sqlalchemy.orm import relationship

class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Foreign Keys
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    post_id = db.Column(
        db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )

    # 답글 기능을 위한 새로운 필드 추가
    parent_id = db.Column(
        db.Integer, db.ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    depth = db.Column(db.Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

    # 답글 관계 설정
    replies = db.relationship(
        "Comment",
        backref=db.backref("parent", remote_side=[id]),
        cascade="all, delete-orphan",
        order_by="Comment.created_at.asc()"
    )

    def __repr__(self):
        return f"<Comment by User {self.user_id} on Post {self.post_id}>"
