from flask import Blueprint, jsonify, request, session
from PIL import Image, ImageDraw, ImageFont
import random
import string
import io

# CAPTCHA 블루프린트 정의
captcha_blueprint = Blueprint('captcha', __name__)

# CAPTCHA 이미지 생성 함수
def generate_captcha_text(length=6):
    """랜덤 텍스트로 CAPTCHA 문자열 생성"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_captcha_image(captcha_text):
    """CAPTCHA 텍스트를 이미지로 변환"""
    width, height = 150, 50
    image = Image.new('RGB', (width, height), (255, 255, 255))  # 흰 배경
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)  # 기본 폰트 대신 truetype 폰트를 사용
    except IOError:
        font = ImageFont.load_default()  # 기본 폰트 사용

    text_width, text_height = draw.textsize(captcha_text, font=font)
    text_position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(text_position, captcha_text, fill=(0, 0, 0), font=font)  # 텍스트 색은 검정

    # 이미지에 난수 추가 (고객 봇 방지용)
    for _ in range(random.randint(50, 100)):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line([x1, y1, x2, y2], fill=(0, 0, 0), width=1)

    return image

# CAPTCHA 이미지 생성 라우트
@captcha_blueprint.route('/generate', methods=['GET'])
def generate_captcha():
    """CAPTCHA 이미지와 텍스트 생성"""
    captcha_text = generate_captcha_text()  # 랜덤 텍스트 생성
    session['captcha_text'] = captcha_text  # 세션에 CAPTCHA 텍스트 저장

    image = generate_captcha_image(captcha_text)  # CAPTCHA 이미지 생성

    # 이미지를 바이트로 변환하여 반환
    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)

    # 이미지 데이터 반환
    return (img_io.getvalue(), 200, {'Content-Type': 'image/png'})

# CAPTCHA 텍스트 검증 라우트
@captcha_blueprint.route('/verify', methods=['POST'])
def verify_captcha():
    """사용자가 입력한 CAPTCHA 텍스트 검증"""
    user_input = request.form.get('captcha_text')

    if not user_input:
        return jsonify({'error': 'CAPTCHA 텍스트를 입력해 주세요.'}), 400
    
    # 세션에서 저장된 CAPTCHA 텍스트와 비교
    if user_input.upper() == session.get('captcha_text', '').upper():
        return jsonify({'success': 'CAPTCHA 인증 성공!'}), 200
    else:
        return jsonify({'error': '잘못된 CAPTCHA 텍스트입니다.'}), 400