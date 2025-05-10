# db_check.py
# 기존 데이터베이스의 구조를 확인하고 필요한 필드를 추가하는 스크립트

from flask import Flask
from db import db, init_app
import pymysql
import os
from dotenv import load_dotenv

# .env 파일 로드
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Flask 앱 생성
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB 초기화
init_app(app)

def check_and_alter_news_table():
    """News 테이블 구조를 확인하고 필요한 필드를 추가합니다."""
    with app.app_context():
        connection = db.engine.raw_connection()
        try:
            cursor = connection.cursor()
            
            # 1. 현재 테이블 구조 확인
            cursor.execute("DESCRIBE news")
            columns = {row[0] for row in cursor.fetchall()}
            print(f"현재 news 테이블 컬럼: {columns}")
            
            # 2. 누락된 필드 확인 및 추가
            required_columns = {
                'image_url': 'VARCHAR(512)',
                'image_path': 'VARCHAR(512)',
                'thumbnail_path': 'VARCHAR(512)',
                'images': 'JSON',
                'author': 'VARCHAR(100)',
                'author_email': 'VARCHAR(150)',
                'source_id': 'VARCHAR(128)',
                'is_deleted': 'BOOLEAN'
            }
            
            # 누락된 컬럼 추가
            for column, data_type in required_columns.items():
                if column not in columns:
                    print(f"'{column}' 컬럼 추가 중...")
                    
                    # default 값 설정
                    default_value = 'NULL'
                    if column == 'is_deleted':
                        default_value = '0'  # false
                    
                    # 컬럼 추가 쿼리 실행
                    try:
                        cursor.execute(f"ALTER TABLE news ADD COLUMN {column} {data_type} DEFAULT {default_value}")
                        print(f"'{column}' 컬럼이 성공적으로 추가되었습니다.")
                    except Exception as e:
                        print(f"'{column}' 컬럼 추가 중 오류 발생: {e}")
            
            # 3. 인덱스 추가 (필요한 경우)
            try:
                cursor.execute("SHOW INDEX FROM news WHERE Key_name = 'idx_source_id'")
                has_source_id_index = cursor.fetchone() is not None
                
                if not has_source_id_index:
                    print("'source_id' 인덱스 추가 중...")
                    cursor.execute("CREATE INDEX idx_source_id ON news (source_id)")
                    print("'source_id' 인덱스가 성공적으로 추가되었습니다.")
            except Exception as e:
                print(f"인덱스 추가 중 오류 발생: {e}")
            
            # 변경사항 저장
            connection.commit()
            print("데이터베이스 변경사항이 성공적으로 저장되었습니다.")
            
        except Exception as e:
            print(f"데이터베이스 구조 확인/수정 중 오류 발생: {e}")
            connection.rollback()
        finally:
            connection.close()

if __name__ == "__main__":
    check_and_alter_news_table()