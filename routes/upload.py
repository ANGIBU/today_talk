# routes/upload.py
from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_login import login_required, current_user
import logging
import uuid

# 로깅 설정
logger = logging.getLogger(__name__)

# 블루프린트 정의
upload_blueprint = Blueprint('upload', __name__, url_prefix='/api')

# 허용된 확장자
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 확장자 허용 여부 확인
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 파일 업로드 라우트
@upload_blueprint.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다.'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '선택된 파일이 없습니다.'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # 안전한 파일명 생성
            original_filename = secure_filename(file.filename)
            filename_parts = original_filename.rsplit('.', 1)
            
            # 타임스탬프와 UUID로 유니크한 파일명 생성
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            new_filename = f"{timestamp}_{unique_id}_{filename_parts[0]}.{filename_parts[1]}"
            
            # 업로드 폴더 확인
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            
            # 파일 저장
            file_path = os.path.join(upload_folder, new_filename)
            file.save(file_path)
            
            # URL 생성
            file_url = f"/static/uploads/{new_filename}"
            
            return jsonify({
                'success': True,
                'url': file_url,
                'filename': new_filename
            })
            
        except Exception as e:
            logger.error(f"파일 업로드 중 오류 발생: {e}")
            return jsonify({'error': '파일 업로드 중 오류가 발생했습니다.'}), 500
    
    return jsonify({'error': '허용되지 않은 파일 형식입니다.'}), 400

# 파일 삭제 라우트
@upload_blueprint.route('/delete-upload', methods=['DELETE'])
@login_required
def delete_upload():
    file_url = request.args.get('url')
    
    if not file_url:
        return jsonify({'error': 'URL이 제공되지 않았습니다.'}), 400
    
    try:
        # URL에서 파일명 추출
        filename = file_url.split('/')[-1]
        
        # 파일 경로 생성
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, filename)
        
        # 파일 존재 여부 확인
        if os.path.exists(file_path):
            # 파일 삭제
            os.remove(file_path)
            return jsonify({'success': True})
        else:
            return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
            
    except Exception as e:
        logger.error(f"파일 삭제 중 오류 발생: {e}")
        return jsonify({'error': '파일 삭제 중 오류가 발생했습니다.'}), 500