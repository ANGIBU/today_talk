## upload.py
# 파일 업로드 유틸리티
import os

def save_file(file, upload_dir):
    """파일 저장"""
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_path = os.path.join(upload_dir, file.filename)
    file.save(file_path)
    return file_path