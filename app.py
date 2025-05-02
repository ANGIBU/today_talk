import os
import sys
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from sqlalchemy.sql import text
from utils.log import setup_logging
from routes import blueprints
from db import db
import threading
import time

# Windows 환경에서 UnicodeEncodeError 방지
sys.stdout.reconfigure(encoding="utf-8")

# 로그 설정
logging.basicConfig(level=logging.ERROR)  # 불필요한 로그 출력 억제

# .env 파일 명시적 로드
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
try:
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        print(f"[INFO] .env 파일 로드 완료: {dotenv_path}")
    else:
        print("[WARNING] .env 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"[ERROR] .env 파일 로드 중 오류 발생: {e}")


def create_app():
    """Flask 애플리케이션 생성 함수""" 
    app = Flask(__name__)

    # 로그 설정
    setup_logging(app)
    app.logger.propagate = False  # 중복 로그 방지

    # 환경 설정 로드
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        app.config.from_object("config.production.ProductionConfig")
    else:
        app.config.from_object("config.development.DevelopmentConfig")

    # 데이터베이스 초기화
    db.init_app(app)
    migrate = Migrate(app, db)

    # 사용자 인증 설정
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "로그인이 필요합니다."

    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return db.session.get(User, int(user_id))

    # 메일 설정
    mail = Mail(app)
    if not app.config.get("MAIL_USERNAME") or not app.config.get("MAIL_PASSWORD"):
        print("[ERROR] 메일 설정이 누락되었습니다. SMTP 설정을 확인하세요.")
        sys.exit(1)

    # CORS 설정
    CORS(app)

    # 블루프린트 등록
    with app.app_context():
        for blueprint in blueprints:
            app.register_blueprint(blueprint)

    # 업로드 폴더 설정 추가
    app.config["UPLOAD_FOLDER"] = "static/uploads"

    # 데이터베이스 연결 테스트
    try:
        with app.app_context():
            db.session.execute(text("SELECT 1"))
            print("[SUCCESS] 데이터베이스 연결 성공")
    except Exception as e:
        print(f"[ERROR] 데이터베이스 연결 실패: {e}")
        sys.exit(1)

    return app


def background_scraper(app):
    """
    5분마다 스크래핑을 실행하는 백그라운드 함수
    """
    from scripts.scrape_naver_news import scrape_naver_news, NAVER_NEWS_CATEGORIES

    while True:
        with app.app_context():
            print("[INFO] 스크래핑 작업 실행 중...")

            # 각 카테고리별 뉴스 스크래핑
            for category, url in NAVER_NEWS_CATEGORIES.items():
                try:
                    scrape_naver_news(url, category)
                    print(f"[SUCCESS] {category} 카테고리 스크래핑 완료")
                except Exception as e:
                    print(f"[ERROR] {category} 카테고리 스크래핑 실패: {e}")

        # 5분(300초)마다 실행
        time.sleep(300)


# 전역 예외 처리: 스택 트레이스 억제
def suppress_traceback(exctype, value, traceback):
    print(f"An error of type {exctype.__name__} occurred. Message: {value}")


sys.excepthook = suppress_traceback

# Flask 애플리케이션 실행
if __name__ == "__main__":
    app = create_app()

    # 예외 핸들러 설정
    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

    # 데이터베이스 테이블 생성 확인
    with app.app_context():
        try:
            db.create_all()  # 테이블이 없으면 생성
            print("[SUCCESS] 데이터베이스 테이블 확인/생성 완료")
        except Exception as e:
            print(f"[ERROR] 데이터베이스 테이블 생성 중 오류 발생: {str(e)}")
            sys.exit(1)

    # 백그라운드 스크래퍼 스레드 시작 (5분마다 실행)
    scraper_thread = threading.Thread(target=background_scraper, args=(app,), daemon=True)
    scraper_thread.start()

    print("[INFO] 애플리케이션 실행 준비 완료")
    app.run(host="0.0.0.0", port=5000, use_reloader=False)
