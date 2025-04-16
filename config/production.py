# config\production.py
import os
from config.base import Config

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "mysql+pymysql://facecom:dks12345@10.0.66.15/PanArchive",
    )
    
    # SQLALCHEMY_DATABASE_URI = os.getenv(
    #     "SQLALCHEMY_DATABASE_URI",
    #     "mysql+pymysql://facecom2000:dks12345@192.168.219.43/PanArchive",
    # )
    
    MAIL_DEBUG = False
    SESSION_COOKIE_SECURE = True
    TESTING = False
    FLASK_ENV = "production"
    PROPAGATE_EXCEPTIONS = True
