# config/development.py
import os
from config.base import Config

class DevelopmentConfig(Config):
    DEBUG = True
    
    # Docker 환경에 맞게 수정
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "mysql+pymysql://livon:dks12345@mysql:3306/today_talk"
    )
    
    MAIL_DEBUG = True
    SESSION_COOKIE_SECURE = False
    TESTING = False
    FLASK_ENV = "development"
    PROPAGATE_EXCEPTIONS = True
    TIMEZONE = "Asia/Seoul"