import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db import db
class ContactService:
    def __init__(self, smtp_server, smtp_port, smtp_user, smtp_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

    def send_contact_email(self, subject, body, from_email, to_email):
        # 이메일 전송
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # 이메일 본문
        msg.attach(MIMEText(body, 'plain'))

        # SMTP 서버 설정
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
