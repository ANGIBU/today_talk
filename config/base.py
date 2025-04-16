# config\base.py
import os

class Config:
    """
    공통 설정을 담고 있는 기본 클래스.
    모든 환경에서 공통적으로 사용할 설정들을 정의합니다.
    """
    # 애플리케이션 보안 설정
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')  # 기본 비밀 키
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() in ['true', '1', 'yes']  # HTTPS 연결에서만 쿠키 사용

    # SQLAlchemy 설정
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # SQLAlchemy 이벤트 시스템 비활성화 (성능 최적화)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///default.db')  # 기본 데이터베이스 URI

    # 업로드 파일 설정
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')  # 업로드 파일 경로
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 파일 업로드 크기 제한 (16MB)

    # 이메일 설정
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')  # 기본 메일 서버
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))  # 메일 서버 포트
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']  # TLS 사용 여부
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', None)  # 메일 사용자 이름
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', None)  # 메일 비밀번호
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')  # 기본 발신자 이메일

    # 기타 설정
    TIMEZONE = os.environ.get('TIMEZONE', 'Asia/Seoul')  # 기본 시간대
