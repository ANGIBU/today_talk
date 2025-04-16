import unittest
from flask import Flask
from services.contact_service import submit_contact_form
from db import app, db
class TestContact(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    def test_submit_contact_form(self):
        with self.app.app_context():
            data = {"subject": "문의 제목", "message": "문의 내용"}
            response = submit_contact_form(data)
            self.assertTrue(response["success"])

if __name__ == "__main__":
    unittest.main()
