# models/user.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from db import db
from sqlalchemy.orm import relationship

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(150), nullable=True, unique=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    # Posts relationship
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    # Comments relationship 추가
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "nickname": self.nickname,
            "created_at": self.created_at
        }

    def __repr__(self):
        return f"<User {self.username}>"