# config/development.py
import os
from config.base import Config


class DevelopmentConfig(Config):
    DEBUG = True

    # 데이터베이스 연결 설정
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "mysql+pymysql://facecom:dks12345@10.0.66.15/PanArchive",
    )

    # 로컬 개발 환경용 데이터베이스 (필요하면 이걸로 변경 가능)
    # SQLALCHEMY_DATABASE_URI = os.getenv(
    #     "SQLALCHEMY_DATABASE_URI", "mysql+pymysql://root@127.0.0.1/panarchive"
    # )

    # SQLALCHEMY_DATABASE_URI = os.getenv(
    #     "SQLALCHEMY_DATABASE_URI",
    #     "mysql+pymysql://facecom2000:dks12345@192.168.219.43/PanArchive",
    # )

    MAIL_DEBUG = True
    SESSION_COOKIE_SECURE = False
    TESTING = False
    FLASK_ENV = "development"
    PROPAGATE_EXCEPTIONS = True

    # 타임존 설정 (필요 시 활성화)
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Seoul")
