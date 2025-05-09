# models/__init__.py
from db import db
from flask_migrate import Migrate

# 전역 변수
migrate = None

def init_db(app):
    """
    Flask 애플리케이션과 SQLAlchemy를 초기화하고 마이그레이션 설정
    """
    global migrate
    
    # DB 초기화
    db.init_app(app)
    
    # 마이그레이션 설정
    migrate = Migrate(app, db)
    
    # 모델 임포트 (순환 참조 방지)
    from models.user import User
    from models.post import Post
    from models.comment import Comment
    from models.news import News
    from models.contact import Contact
    from models.login_attempts import LoginAttempt
    from models.captcha import Captcha
    
    return db