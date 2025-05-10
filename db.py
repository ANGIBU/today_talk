# db.py
from flask_sqlalchemy import SQLAlchemy
import os
import time
from sqlalchemy.exc import OperationalError
import logging

# SQLAlchemy 객체 생성
db = SQLAlchemy()

def init_app(app):
    """Flask 애플리케이션과 SQLAlchemy를 연결하고 초기화"""
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    
    if not db_uri:
        raise RuntimeError("❌ SQLALCHEMY_DATABASE_URI가 설정되지 않았습니다!")
    
    # .env 환경변수가 있으면 적용
    if os.environ.get('SQLALCHEMY_DATABASE_URI'):
        db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        print(f"[INFO] 환경변수에서 데이터베이스 URI 로드: {db_uri}")
    
    # Flask 앱 설정
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = app.config.get('SQLALCHEMY_ECHO', False)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,  # 연결 유효성 검사
        'pool_recycle': 3600,   # 1시간마다 연결 재생성
        'connect_args': {
            'connect_timeout': 10  # 연결 타임아웃 10초
        }
    }
    
    # DB 연결 초기화
    db.init_app(app)
    
    # 연결 재시도 로직
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # 연결 테스트
                db.engine.connect()
                print(f"[SUCCESS] 데이터베이스 연결 성공: {db_uri}")
                return
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"[WARNING] 데이터베이스 연결 실패 ({attempt+1}/{max_retries}): {e}")
                print(f"[INFO] {retry_delay}초 후 재시도...")
                time.sleep(retry_delay)
            else:
                print(f"[ERROR] 데이터베이스 연결 실패: {e}")
                raise