# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from models.login_attempts import LoginAttempt
from db import db
from services.auth_service import register_user, authenticate_user, send_reset_email
from services.user_service import check_duplicate
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 정의
auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')

# 로그인 라우트
@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember_me = 'remember_me' in request.form
        
        if not username or not password:
            flash('아이디와 비밀번호를 모두 입력하세요.', 'danger')
            return render_template('auth/login.html')
        
        # 사용자 인증
        user = authenticate_user(
            username, 
            password, 
            request.remote_addr, 
            request.user_agent.string
        )
        
        if user:
            login_user(user, remember=remember_me)
            flash('로그인 성공!', 'success')
            logger.info(f"User {username} logged in successfully.")
            
            # 로그인 후 이전 페이지로 리다이렉트
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home.index'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'danger')
            logger.warning(f"Failed login attempt for username: {username}")
            
    return render_template('auth/login.html')

# 회원가입 라우트
@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
        
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            password_confirm = request.form.get('password_confirm', '').strip()
            nickname = request.form.get('nickname', '').strip()
            
            # 필수 필드 확인
            if not email or not username or not password or not nickname:
                flash('모든 필드를 입력해주세요.', 'danger')
                return redirect(url_for('auth.register'))
                
            # 비밀번호 확인
            if password != password_confirm:
                flash('비밀번호가 일치하지 않습니다.', 'danger')
                return redirect(url_for('auth.register'))
                
            # 길이 확인
            if len(username) < 4 or len(username) > 16:
                flash('아이디는 4~16자 이내여야 합니다.', 'danger')
                return redirect(url_for('auth.register'))
                
            if len(password) < 8 or len(password) > 20:
                flash('비밀번호는 8~20자 이내여야 합니다.', 'danger')
                return redirect(url_for('auth.register'))
                
            if len(nickname) < 3 or len(nickname) > 8:
                flash('닉네임은 3~8자 이내여야 합니다.', 'danger')
                return redirect(url_for('auth.register'))
            
            # 사용자 등록
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
            
    return render_template('auth/login.html')

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

# 아이디 중복 확인 API
@auth_blueprint.route('/check-id', methods=['POST'])
def check_id():
    data = request.get_json()
    username = data.get('username', '').strip() if data else ''
    
    if not username:
        return jsonify({'success': False, 'message': '아이디를 입력하세요.'}), 400
        
    is_duplicate = check_duplicate('username', username)
    return jsonify({'success': True, 'is_duplicate': is_duplicate})

# 이메일 중복 확인 API
@auth_blueprint.route('/check-email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email', '').strip() if data else ''
    
    if not email:
        return jsonify({'success': False, 'message': '이메일을 입력하세요.'}), 400
        
    is_duplicate = check_duplicate('email', email)
    return jsonify({'success': True, 'is_duplicate': is_duplicate})

# 닉네임 중복 확인 API
@auth_blueprint.route('/check-nickname', methods=['POST'])
def check_nickname():
    data = request.get_json()
    nickname = data.get('nickname', '').strip() if data else ''
    
    if not nickname:
        return jsonify({'success': False, 'message': '닉네임을 입력하세요.'}), 400
        
    is_duplicate = check_duplicate('nickname', nickname)
    return jsonify({'success': True, 'is_duplicate': is_duplicate})