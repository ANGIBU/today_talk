# routes/profile.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models.user import User
from models.post import Post
from models.comment import Comment
from db import db
from services.user_service import update_user_profile, upload_profile_image
from werkzeug.security import generate_password_hash
import os
from datetime import datetime
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 블루프린트 정의
profile_blueprint = Blueprint('profile', __name__, url_prefix='/profile')

# 프로필 페이지
@profile_blueprint.route('/')
@login_required
def index():
    # 사용자 작성 게시글
    posts = Post.query.filter_by(user_id=current_user.id).order_by(
        Post.created_at.desc()
    ).limit(5).all()
    
    # 사용자 작성 댓글
    comments = Comment.query.filter_by(user_id=current_user.id).order_by(
        Comment.created_at.desc()
    ).limit(10).all()
    
    return render_template(
        'profile/profile.html',
        user=current_user,
        posts=posts,
        comments=comments
    )

# 다른 사용자 프로필 페이지
@profile_blueprint.route('/<int:user_id>')
def user_profile(user_id):
    # 현재 사용자 확인
    if user_id == current_user.id:
        return redirect(url_for('profile.index'))
    
    user = User.query.get_or_404(user_id)
    
    # 사용자 작성 게시글
    posts = Post.query.filter_by(user_id=user.id).order_by(
        Post.created_at.desc()
    ).limit(5).all()
    
    return render_template(
        'profile/user_profile.html',
        user=user,
        posts=posts
    )

# 프로필 수정 페이지
@profile_blueprint.route('/edit', methods=['GET'])
@login_required
def edit():
    return render_template('profile/edit.html', user=current_user)

# 프로필 수정 처리
@profile_blueprint.route('/edit', methods=['POST'])
@login_required
def update():
    # 폼 데이터 가져오기
    nickname = request.form.get('nickname', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    
    # 필수 필드 확인
    if not nickname or not email:
        flash('닉네임과 이메일은 필수 항목입니다.', 'danger')
        return redirect(url_for('profile.edit'))
    
    # 프로필 이미지 처리
    profile_image = request.files.get('profile_image')
    if profile_image and profile_image.filename:
        success, message = upload_profile_image(current_user.id, profile_image)
        if not success:
            flash(f'프로필 이미지 업로드 실패: {message}', 'danger')
    
    # 사용자 정보 업데이트
    data = {
        'nickname': nickname,
        'email': email
    }
    
    # 비밀번호 변경 (입력한 경우에만)
    if password:
        data['password'] = password
    
    success, message = update_user_profile(current_user.id, data)
    
    if success:
        flash('프로필이 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('profile.index'))
    else:
        flash(f'프로필 수정 실패: {message}', 'danger')
        return redirect(url_for('profile.edit'))

# 내 게시글 목록
@profile_blueprint.route('/posts')
@login_required
def my_posts():
    page = request.args.get('page', 1, type=int)
    
    posts = Post.query.filter_by(user_id=current_user.id).order_by(
        Post.created_at.desc()
    ).paginate(page=page, per_page=10, error_out=False)
    
    return render_template('profile/my_posts.html', posts=posts)

# 내 댓글 목록
@profile_blueprint.route('/comments')
@login_required
def my_comments():
    page = request.args.get('page', 1, type=int)
    
    comments = Comment.query.filter_by(user_id=current_user.id).order_by(
        Comment.created_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('profile/my_comments.html', comments=comments)

# 비밀번호 변경 페이지
@profile_blueprint.route('/change-password', methods=['GET'])
@login_required
def change_password():
    return render_template('profile/change_password.html')

# 비밀번호 변경 처리
@profile_blueprint.route('/change-password', methods=['POST'])
@login_required
def update_password():
    # 폼 데이터 가져오기
    current_password = request.form.get('current_password', '').strip()
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    
    # 입력 확인
    if not current_password or not new_password or not confirm_password:
        flash('모든 필드를 입력해주세요.', 'danger')
        return redirect(url_for('profile.change_password'))
    
    # 현재 비밀번호 확인
    if not current_user.check_password(current_password):
        flash('현재 비밀번호가 일치하지 않습니다.', 'danger')
        return redirect(url_for('profile.change_password'))
    
    # 새 비밀번호 확인
    if new_password != confirm_password:
        flash('새 비밀번호가 일치하지 않습니다.', 'danger')
        return redirect(url_for('profile.change_password'))
    
    # 비밀번호 길이 확인
    if len(new_password) < 8:
        flash('비밀번호는 8자 이상이어야 합니다.', 'danger')
        return redirect(url_for('profile.change_password'))
    
    try:
        # 비밀번호 업데이트
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('비밀번호가 성공적으로 변경되었습니다.', 'success')
        return redirect(url_for('profile.index'))
    except Exception as e:
        logger.error(f"비밀번호 변경 중 오류 발생: {e}")
        db.session.rollback()
        flash('비밀번호 변경 중 오류가 발생했습니다. 다시 시도해주세요.', 'danger')
        return redirect(url_for('profile.change_password'))

# 계정 삭제 페이지
@profile_blueprint.route('/delete-account', methods=['GET'])
@login_required
def delete_account_page():
    return render_template('profile/delete_account.html')

# 계정 삭제 처리
@profile_blueprint.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    # 비밀번호 확인
    password = request.form.get('password', '').strip()
    
    if not password:
        flash('비밀번호를 입력해주세요.', 'danger')
        return redirect(url_for('profile.delete_account_page'))
    
    # 비밀번호 검증
    if not current_user.check_password(password):
        flash('비밀번호가 일치하지 않습니다.', 'danger')
        return redirect(url_for('profile.delete_account_page'))
    
    try:
        # 사용자 삭제 (관계 설정으로 게시글과 댓글도 함께 삭제됨)
        db.session.delete(current_user._get_current_object())
        db.session.commit()
        
        flash('계정이 성공적으로 삭제되었습니다.', 'success')
        return redirect(url_for('home.index'))
    except Exception as e:
        logger.error(f"계정 삭제 중 오류 발생: {e}")
        db.session.rollback()
        flash('계정 삭제 중 오류가 발생했습니다. 다시 시도해주세요.', 'danger')
        return redirect(url_for('profile.delete_account_page'))