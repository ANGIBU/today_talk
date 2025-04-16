import random
import string
import io
from PIL import Image, ImageDraw, ImageFont
import captcha
from db import db
class CaptchaService:
    def __init__(self):
        self.characters = string.ascii_uppercase + string.digits

    def generate_captcha(self):
        # CAPTCHA 문자열 생성
        captcha_text = ''.join(random.choices(self.characters, k=6))
        
        # CAPTCHA 이미지 생성
        image = Image.new('RGB', (150, 50), color='white')
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        draw.text((10, 10), captcha_text, font=font, fill='black')

        # CAPTCHA 이미지 반환
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return captcha_text, img_byte_arr

    def verify_captcha(self, user_input, correct_captcha):
        # CAPTCHA 검증
        return user_input.strip().upper() == correct_captcha.strip().upper()
