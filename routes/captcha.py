# routes/captcha.py
from flask import Blueprint, request, session, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
import random
import string
import io
from datetime import datetime, timedelta
from models.captcha import Captcha
from db import db
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 블루프린트 정의
captcha_blueprint = Blueprint('captcha', __name__, url_prefix='/captcha')

# CAPTCHA 이미지 생성
def generate_captcha_text(length=6):
    """랜덤 CAPTCHA 문자열 생성"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_captcha_image(text):
    """CAPTCHA 이미지 생성"""
    width, height = 200, 80
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    try:
        # 폰트 로드 시도
        font = ImageFont.truetype('arial.ttf', size=36)
    except IOError:
        # 기본 폰트 사용
        font = ImageFont.load_default()
    
    # 텍스트 위치 계산
    text_width, text_height = 0, 0
    try:
        # PIL 버전에 따라 메서드가 다를 수 있음
        text_width, text_height = draw.textsize(text, font=font)
    except AttributeError:
        try:
            text_width, text_height = font.getsize(text)
        except:
            # 기본값 사용
            text_width, text_height = len(text) * 15, 30
    
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    # 텍스트 그리기
    draw.text((text_x, text_y), text, fill=(0, 0, 0), font=font)
    
    # 랜덤 선 그리기 (노이즈)
    for _ in range(8):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=(128, 128, 128), width=2)
    
    # 랜덤 점 그리기 (노이즈)
    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=(128, 128, 128))
    
    # 이미지 왜곡 (약간 변형)
    image = image.transform(
        (width, height),
        Image.AFFINE,
        (1, random.uniform(-0.1, 0.1), 0,
         random.uniform(-0.1, 0.1), 1, 0),
        Image.BICUBIC
    )
    
    # 이미지를 바이트 데이터로 변환
    image_io = io.BytesIO()
    image.save(image_io, format='PNG')
    image_io.seek(0)
    
    return image_io

# CAPTCHA 이미지 라우트
@captcha_blueprint.route('/', methods=['GET'])
def captcha():
    # CAPTCHA 문자열 생성
    captcha_text = generate_captcha_text()
    
    # 세션에 CAPTCHA 저장
    session['captcha_text'] = captcha_text
    session['captcha_time'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    # DB에 CAPTCHA 저장 (선택사항)
    try:
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        captcha_entry = Captcha(
            text=captcha_text,
            session_id=session.sid,
            expires_at=expires_at
        )
        db.session.add(captcha_entry)
        db.session.commit()
    except Exception as e:
        logger.error(f"CAPTCHA 저장 중 오류 발생: {e}")
        db.session.rollback()
    
    # CAPTCHA 이미지 생성 및 반환
    image_io = generate_captcha_image(captcha_text)
    return send_file(image_io, mimetype='image/png')

# CAPTCHA 검증 라우트
@captcha_blueprint.route('/verify', methods=['POST'])
def verify():
    user_input = request.form.get('captcha', '').strip().upper()
    captcha_text = session.get('captcha_text', '').upper()
    captcha_time_str = session.get('captcha_time')
    
    # 입력 확인
    if not user_input:
        return jsonify({'success': False, 'message': 'CAPTCHA를 입력해주세요.'}), 400
    
    # 시간 확인 (10분 이내)
    if captcha_time_str:
        captcha_time = datetime.strptime(captcha_time_str, '%Y-%m-%d %H:%M:%S')
        if datetime.utcnow() - captcha_time > timedelta(minutes=10):
            # 새 CAPTCHA 생성
            session.pop('captcha_text', None)
            session.pop('captcha_time', None)
            return jsonify({
                'success': False, 
                'message': 'CAPTCHA가 만료되었습니다. 새로고침 후 다시 시도해주세요.',
                'expired': True
            }), 400
    
    # CAPTCHA 검증
    if user_input == captcha_text:
        # 성공 후 세션에서 제거
        session.pop('captcha_text', None)
        session.pop('captcha_time', None)
        
        # DB에서 CAPTCHA 사용 처리 (선택사항)
        try:
            captcha_entry = Captcha.query.filter_by(
                text=captcha_text, 
                session_id=session.sid,
                is_used=False
            ).first()
            
            if captcha_entry:
                captcha_entry.is_used = True
                db.session.commit()
        except Exception as e:
            logger.error(f"CAPTCHA 사용 처리 중 오류 발생: {e}")
            db.session.rollback()
        
        return jsonify({'success': True, 'message': 'CAPTCHA 인증 성공!'})
    else:
        return jsonify({'success': False, 'message': '잘못된 CAPTCHA입니다.'}), 400

# CAPTCHA 새로고침 라우트
@captcha_blueprint.route('/refresh', methods=['GET'])
def refresh():
    # 기존 CAPTCHA 세션 제거
    session.pop('captcha_text', None)
    session.pop('captcha_time', None)
    
    # 새 CAPTCHA 생성 및 반환
    return captcha()