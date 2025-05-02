from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required
from models.user import User
from db import db
from services.auth_utils import register_user, authenticate_user, send_reset_email, check_duplicate
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')

# 로그인 라우트
@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            logger.error("Username or password not provided in login attempt.")
            flash('아이디와 비밀번호를 모두 입력하세요.', 'danger')
            return render_template('auth/login.html')

        user = authenticate_user(username, password)
        if user:
            login_user(user)
            flash('로그인 성공!', 'success')
            logger.info(f"User {username} logged in successfully.")
            # 로그인 후 이전 페이지로 리다이렉트 (next 파라미터 활용)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home.index'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'danger')
            logger.warning(f"Failed login attempt for username: {username}")
    return render_template('auth/login.html')

# 회원가입 라우트
@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            nickname = request.form.get('nickname', '').strip()

            if not email or not username or not password or not nickname:
                logger.error("Missing required registration fields.")
                flash('모든 필드를 입력해주세요.', 'danger')
                return redirect(url_for('auth.register'))

            if len(username) < 3 or len(password) < 6 or len(nickname) < 3:
                flash('아이디, 비밀번호 또는 닉네임이 너무 짧습니다.', 'danger')
                return redirect(url_for('auth.register'))

            result, message = register_user(email, username, password, nickname)

            if result:
                flash('회원가입이 완료되었습니다. 로그인하세요.', 'success')
                logger.info(f"User {email} registered successfully.")
                return redirect(url_for('auth.login'))
            else:
                flash(message, 'danger')
                logger.warning(f"Registration failed for email: {email} - {message}")
                return redirect(url_for('auth.register'))

        except Exception as e:
            logger.error(f"Error during registration: {e}")
            flash('회원가입 중 오류가 발생했습니다. 다시 시도해주세요.', 'danger')
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html')

# 로그아웃 라우트
@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃되었습니다.', 'success')
    logger.info("User logged out successfully.")
    return redirect(request.referrer or url_for('home.index'))

# 비밀번호 재설정 라우트
@auth_blueprint.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not email or '@' not in email:
            flash('유효한 이메일 주소를 입력하세요.', 'danger')
            logger.error("Invalid email format provided for password reset.")
            return render_template('auth/reset_password.html')

        if send_reset_email(email):
            flash('비밀번호 재설정 링크가 이메일로 전송되었습니다.', 'info')
            logger.info(f"Password reset email sent to: {email}")
        else:
            flash('입력한 이메일을 찾을 수 없습니다.', 'danger')
            logger.warning(f"Failed to send password reset email to: {email}")
    return render_template('auth/reset_password.html')

# 중복 확인 라우트
@auth_blueprint.route('/check_duplicate', methods=['GET'])
def check_duplicate_route():
    field = request.args.get('field')
    value = request.args.get('value')

    if not field or not value:
        return jsonify({'success': False, 'message': 'Invalid parameters'}), 400

    try:
        is_duplicate = check_duplicate(field, value)
        return jsonify({'success': True, 'is_duplicate': is_duplicate})
    except ValueError as e:
        logger.error(f"Invalid field for duplicate check: {field}")
        return jsonify({'success': False, 'message': str(e)}), 400
