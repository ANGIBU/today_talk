import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    # 로그 파일 경로 설정
    log_directory = 'logs'
    log_file = os.path.join(log_directory, 'panarchive.log')
    
    # logs 폴더가 없으면 생성
    try:
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
    except OSError as e:
        return  # 오류 메시지를 출력하지 않음
    
    # 로그 롤링 설정
    try:
        handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=3, delay=True)  # 최대 10MB, 백업 3개
        handler.setLevel(logging.INFO)
    except Exception as e:
        return  # 오류 메시지를 출력하지 않음

    # 로그 포맷 설정
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # 애플리케이션 로거 설정
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    # 첫 번째 로그 메시지 (주석 처리하여 출력하지 않음)
    # app.logger.info('PanArchive 애플리케이션 시작')
