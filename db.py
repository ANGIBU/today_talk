# db.py
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy 객체 생성
db = SQLAlchemy()

def init_app(app):
    """Flask 애플리케이션과 SQLAlchemy를 연결하고 초기화"""
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    
    if not db_uri:
        raise RuntimeError("❌ SQLALCHEMY_DATABASE_URI가 설정되지 않았습니다!")
    
    # Flask 앱 설정
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = app.config.get('SQLALCHEMY_ECHO', False)
    
    # DB 연결 초기화
    db.init_app(app)