# scripts/image_utils.py
import os
import uuid
import requests
from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger('news_scraper')

def download_image(image_url, upload_folder, max_size=(800, 800), thumb_size=(200, 200)):
    """
    이미지 URL에서 이미지를 다운로드하고 썸네일을 생성합니다.
    
    Args:
        image_url (str): 다운로드할 이미지 URL
        upload_folder (str): 이미지를 저장할 폴더 경로
        max_size (tuple): 원본 이미지의 최대 크기 (가로, 세로)
        thumb_size (tuple): 썸네일 크기 (가로, 세로)
        
    Returns:
        tuple: (원본 이미지 경로, 썸네일 경로) 또는 실패 시 (None, None)
    """
    if not image_url:
        return None, None
        
    try:
        # 이미지를 저장할 폴더 생성
        os.makedirs(upload_folder, exist_ok=True)
        os.makedirs(os.path.join(upload_folder, 'thumbs'), exist_ok=True)
        
        # 고유한 파일명 생성
        unique_filename = f"{uuid.uuid4().hex}.jpg"
        image_path = os.path.join(upload_folder, unique_filename)
        thumb_path = os.path.join(upload_folder, 'thumbs', unique_filename)
        
        # User-Agent 헤더 추가
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 이미지 다운로드
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 이미지 처리
        img = Image.open(BytesIO(response.content))
        
        # 이미지 포맷 확인 및 변환
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # 원본 이미지 크기 조정 (필요한 경우)
        img.thumbnail(max_size, Image.LANCZOS)
        img.save(image_path, 'JPEG', quality=90)
        
        # 썸네일 생성
        thumb_img = img.copy()
        thumb_img.thumbnail(thumb_size, Image.LANCZOS)
        thumb_img.save(thumb_path, 'JPEG', quality=80)
        
        # 상대 경로로 반환 (static 폴더 기준)
        relative_image_path = os.path.relpath(image_path, 'static')
        relative_thumb_path = os.path.relpath(thumb_path, 'static')
        
        return relative_image_path, relative_thumb_path
        
    except Exception as e:
        logger.error(f"이미지 다운로드/처리 중 오류 발생: {str(e)} - URL: {image_url}")
        return None, None