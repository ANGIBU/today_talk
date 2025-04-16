import unittest
from flask import Flask
from services.faq_service import get_faq_list
from db import db, init_app  # db 및 init_app을 임포트

class TestFAQ(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        init_app(self.app)  # db 초기화
        self.client = self.app.test_client()

    def test_get_faq_list(self):
        with self.app.app_context():
            faqs = get_faq_list()
            self.assertIsInstance(faqs, list)
            self.assertGreaterEqual(len(faqs), 0)

if __name__ == "__main__":
    unittest.main()
