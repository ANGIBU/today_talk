from flask import Blueprint

# 기존 블루프린트 가져오기
from .home import home_blueprint
from .auth import auth_blueprint
from .profile import profile_blueprint
from .contact import contact_blueprint
from .posts import posts_blueprint
from .comments import comments_blueprint
from .news import news_blueprint
from .upload import upload_blueprint

# 새 블루프린트 가져오기
from api.check_id import check_id_blueprint
from api.check_nickname import check_nickname_blueprint
from api.check_email import check_email_blueprint


# 블루프린트 목록을 리스트로 정의
blueprints: list[Blueprint] = [
    home_blueprint,
    auth_blueprint,
    profile_blueprint,
    contact_blueprint,
    posts_blueprint,
    comments_blueprint,
    news_blueprint,
    upload_blueprint,
    # 새 블루프린트 추가
    check_id_blueprint,
    check_nickname_blueprint,
    check_email_blueprint,
]
