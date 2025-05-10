# app.py
import os
import sys
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from sqlalchemy.sql import text
from utils.log import setup_logging
from routes import blueprints
from db import db, init_app
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
    env = os.getenv("FLASK_ENV", "production")  # 기본값을 production으로 변경
    if env == "production":
        app.config.from_object("config.production.ProductionConfig")
    else:
        app.config.from_object("config.development.DevelopmentConfig")

    # 데이터베이스 초기화 - 개선된 init_app 함수 사용
    init_app(app)
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
        # 경고만 표시하고 계속 진행 (sys.exit 제거)
        print("[WARNING] 메일 기능이 비활성화됩니다.")

    # CORS 설정
    CORS(app)

    # 블루프린트 등록
    with app.app_context():
        for blueprint in blueprints:
            app.register_blueprint(blueprint)

    # 업로드 폴더 설정 추가
    app.config["UPLOAD_FOLDER"] = "static/uploads"
    
    # 업로드 폴더가 없으면 생성
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # favicon.ico 경로 추가
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    # 404, 500 에러 핸들러 추가
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({"error": "페이지를 찾을 수 없습니다."}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500

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

    # 데이터베이스 테이블 생성 확인
    with app.app_context():
        try:
            db.create_all()  # 테이블이 없으면 생성
            print("[SUCCESS] 데이터베이스 테이블 확인/생성 완료")
        except Exception as e:
            print(f"[ERROR] 데이터베이스 테이블 생성 중 오류 발생: {str(e)}")
            print("[WARNING] 데이터베이스 테이블 생성을 건너뛰고 계속 진행합니다.")

    # 백그라운드 스크래퍼 스레드 시작 (5분마다 실행)
    try:
        scraper_thread = threading.Thread(target=background_scraper, args=(app,), daemon=True)
        scraper_thread.start()
        print("[INFO] 백그라운드 스크래퍼 스레드 시작 완료")
    except Exception as e:
        print(f"[ERROR] 백그라운드 스크래퍼 시작 실패: {e}")
        print("[WARNING] 백그라운드 스크래퍼 없이 계속 진행합니다.")

    print("[INFO] 애플리케이션 실행 준비 완료")
    # 호스트와 포트 설정 변경 - 환경변수로 포트 설정 가능하도록 수정
    port = int(os.getenv("PORT", 5003))
    app.run(host="0.0.0.0", port=port, debug=(os.getenv("FLASK_ENV", "production") == "development"), use_reloader=False)