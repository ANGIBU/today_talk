## captcha.py
# 캡차 생성 및 검증 유틸리티
import random
import string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def generate_captcha_text(length=6):
    """랜덤 캡차 문자열 생성"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_captcha_image(text):
    """텍스트 기반 캡차 이미지 생성"""
    width, height = 200, 70
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    font = ImageFont.truetype('arial.ttf', size=36)
    draw = ImageDraw.Draw(image)

    # 텍스트를 이미지에 추가
    draw.text((50, 15), text, font=font, fill=(0, 0, 0))

    # 이미지 저장
    output = BytesIO()
    image.save(output, format='PNG')
    output.seek(0)
    return output