import unittest
from utils.captcha import generate_captcha_text, generate_captcha_image
from db import app, db

class TestCaptcha(unittest.TestCase):
    def test_generate_captcha_text(self):
        """CAPTCHA 텍스트 생성 테스트"""
        text = generate_captcha_text()
        self.assertEqual(len(text), 6)  # 기본 길이 6
        self.assertTrue(text.isalnum())  # 알파벳과 숫자로만 구성

    def test_generate_captcha_image(self):
        """CAPTCHA 이미지 생성 테스트"""
        text = "ABC123"
        image = generate_captcha_image(text)
        self.assertIsNotNone(image)  # 이미지 생성 확인
        self.assertTrue(hasattr(image, 'save'))  # 이미지 객체인지 확인


if __name__ == "__main__":
    unittest.main()
