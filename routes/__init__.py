# routes/__init__.py
from flask import Blueprint

# 애플리케이션의 모든 블루프린트 가져오기
from .home import home_blueprint
from .auth import auth_blueprint
from .profile import profile_blueprint
from .posts import posts_blueprint
from .comments import comments_blueprint
from .news import news_blueprint
from .contact import contact_blueprint
from .captcha import captcha_blueprint
from .upload import upload_blueprint

# API 블루프린트 추가
from api.check_id import check_id_blueprint
from api.check_email import check_email_blueprint
from api.check_nickname import check_nickname_blueprint

# 라우트 블루프린트 목록
blueprints = [
    home_blueprint,
    auth_blueprint,
    profile_blueprint,
    posts_blueprint,
    comments_blueprint,
    news_blueprint,
    contact_blueprint,
    captcha_blueprint,
    upload_blueprint,
    
    # API 블루프린트
    check_id_blueprint,
    check_email_blueprint,
    check_nickname_blueprint
]