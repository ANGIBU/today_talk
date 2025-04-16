# models/__init__.py
from flask_migrate import Migrate
from sqlalchemy import text
from db import db  # ✅ `db.py`에서 가져오도록 변경

migrate = None  # Flask-Migrate 전역 변수

def init_db(app):
    """
    Flask 앱과 SQLAlchemy를 초기화하고,
    Migrate를 설정합니다.
    """
    global migrate  # 전역 변수 `migrate` 사용
    db.init_app(app)
    migrate = Migrate(app, db)

    # 데이터베이스 연결 테스트
    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))  # 연결 테스트 쿼리
            print("✅ 데이터베이스 연결 성공")
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")

    # 모델 임포트 (순환 참조 방지)
    from models.user import User
    from models.post import Post
    from models.comment import Comment
    from models.news import News  # 🔹 News 모델 추가 (존재하면)
