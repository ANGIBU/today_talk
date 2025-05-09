# config/production.py
import os
from config.base import Config

class ProductionConfig(Config):
    DEBUG = False
    
    # Docker 환경에 맞게 수정
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "mysql+pymysql://livon:dks12345@mysql:3306/today_talk"
    )
    
    MAIL_DEBUG = False
    SESSION_COOKIE_SECURE = True
    TESTING = False
    FLASK_ENV = "production"
    PROPAGATE_EXCEPTIONS = True