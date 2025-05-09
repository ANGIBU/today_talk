# routes/posts.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from models.post import Post
from models.comment import Comment
from db import db
from services.post_service import (
    get_all_posts, get_post_by_id, create_post, update_post, 
    delete_post, increment_view_count, get_popular_posts, 
    save_post_images
)
from services.comment_service import get_comments_for_post
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 블루프린트 정의
posts_blueprint = Blueprint('posts', __name__, url_prefix='/posts')

# 게시글 목록 조회
@posts_blueprint.route('/<string:category>')
def get_posts(category):
    page = request.args.get('page', 1, type=int)
    
    # 카테고리 별 게시글 조회
    if category == 'popular':
        # 인기 게시글 (7일 내 작성된 게시글 중 조회수 순)
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        popular_free = Post.query.filter(
            Post.category == 'free',
            Post.created_at >= cutoff_date
        ).order_by(Post.views.desc()).limit(10).all()
        
        popular_humor = Post.query.filter(
            Post.category == 'humor',
            Post.created_at >= cutoff_date
        ).order_by(Post.views.desc()).limit(10).all()
        
        popular_info = Post.query.filter(
            Post.category == 'info',
            Post.created_at >= cutoff_date
        ).order_by(Post.views.desc()).limit(10).all()
        
        return render_template(
            'posts/posts_popular.html',
            popular_free=popular_free,
            popular_humor=popular_humor,
            popular_info=popular_info
        )
    else:
        # 일반 게시글 (카테고리별 또는 전체)
        query = Post.query
        
        if category != 'all':
            query = query.filter_by(category=category)
            
        posts = query.order_by(Post.created_at.desc()).paginate(
            page=page, per_page=10, error_out=False
        )
        
        template_name = f'posts/posts_{category}.html'
        return render_template(template_name, posts=posts)

# 게시글 상세 조회
@posts_blueprint.route('/<int:post_id>')
def detail_post(post_id):
    post = get_post_by_id(post_id)
    
    if not post:
        flash('존재하지 않는 게시글입니다.', 'danger')
        return redirect(url_for('posts.get_posts', category='all'))
    
    # 조회수 증가
    increment_view_count(post_id)
    
    # 댓글 목록 조회
    comments = get_comments_for_post(post_id)
    
    return render_template(
        'posts/detail.html',
        post=post,
        comments=comments
    )

# 게시글 작성 페이지
@posts_blueprint.route('/create', methods=['GET'])
@login_required
def add_post():
    return render_template('posts/add.html')

# 게시글 작성 처리
@posts_blueprint.route('/create', methods=['POST'])
@login_required
def create_post_route():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    category = request.form.get('category', '').strip()
    
    if not title or not content or not category:
        flash('제목과 내용, 카테고리를 모두 입력해주세요.', 'danger')
        return redirect(url_for('posts.add_post'))
    
    # 이미지 파일 처리
    files = request.files.getlist('file')
    images = save_post_images(files)
    
    # 게시글 생성
    success, result = create_post(
        title=title,
        content=content,
        category=category,
        user_id=current_user.id,
        images=images
    )
    
    if success:
        flash('게시글이 성공적으로 작성되었습니다.', 'success')
        return redirect(url_for('posts.detail_post', post_id=result.id))
    else:
        flash(f'게시글 작성 중 오류가 발생했습니다: {result}', 'danger')
        return redirect(url_for('posts.add_post'))

# 게시글 수정 페이지
@posts_blueprint.route('/<int:post_id>/edit', methods=['GET'])
@login_required
def edit_post(post_id):
    post = get_post_by_id(post_id)
    
    if not post:
        flash('존재하지 않는 게시글입니다.', 'danger')
        return redirect(url_for('posts.get_posts', category='all'))
    
    # 작성자 권한 확인
    if post.user_id != current_user.id:
        flash('수정 권한이 없습니다.', 'danger')
        return redirect(url_for('posts.detail_post', post_id=post_id))
    
    return render_template('posts/edit.html', post=post)

# 게시글 수정 처리
@posts_blueprint.route('/<int:post_id>/edit', methods=['POST'])
@login_required
def update_post_route(post_id):
    post = get_post_by_id(post_id)
    
    if not post:
        flash('존재하지 않는 게시글입니다.', 'danger')
        return redirect(url_for('posts.get_posts', category='all'))
    
    # 작성자 권한 확인
    if post.user_id != current_user.id:
        flash('수정 권한이 없습니다.', 'danger')
        return redirect(url_for('posts.detail_post', post_id=post_id))
    
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    
    if not title or not content:
        flash('제목과 내용을 모두 입력해주세요.', 'danger')
        return redirect(url_for('posts.edit_post', post_id=post_id))
    
    # 새 이미지 파일 처리
    files = request.files.getlist('file')
    if files and files[0].filename:
        new_images = save_post_images(files)
        
        # 기존 이미지와 새 이미지 합치기
        existing_images = post.images or []
        images = existing_images + new_images
    else:
        images = post.images
    
    # 게시글 수정
    success, result = update_post(
        post_id=post_id,
        title=title,
        content=content,
        images=images
    )
    
    if success:
        flash('게시글이 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('posts.detail_post', post_id=post_id))
    else:
        flash(f'게시글 수정 중 오류가 발생했습니다: {result}', 'danger')
        return redirect(url_for('posts.edit_post', post_id=post_id))

# 게시글 삭제 처리
@posts_blueprint.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post_route(post_id):
    post = get_post_by_id(post_id)
    
    if not post:
        flash('존재하지 않는 게시글입니다.', 'danger')
        return redirect(url_for('posts.get_posts', category='all'))
    
    # 작성자 권한 확인
    if post.user_id != current_user.id:
        flash('삭제 권한이 없습니다.', 'danger')
        return redirect(url_for('posts.detail_post', post_id=post_id))
    
    category = post.category
    
    # 게시글 삭제
    success, message = delete_post(post_id)
    
    if success:
        flash('게시글이 성공적으로 삭제되었습니다.', 'success')
        return redirect(url_for('posts.get_posts', category=category))
    else:
        flash(f'게시글 삭제 중 오류가 발생했습니다: {message}', 'danger')
        return redirect(url_for('posts.detail_post', post_id=post_id))

# 이미지 업로드 API
@posts_blueprint.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '파일이 없습니다.'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': '선택된 파일이 없습니다.'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        new_filename = f"{timestamp}_{filename}"
        
        # 업로드 폴더 확인 및 생성
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        # 파일 저장
        file.save(os.path.join(upload_folder, new_filename))
        
        # 이미지 URL 반환
        image_url = url_for('static', filename=f'uploads/{new_filename}')
        
        return jsonify({'success': True, 'url': image_url, 'filename': new_filename})
    
    return jsonify({'success': False, 'message': '파일 업로드 실패'}), 500

# 인기 게시글 API
@posts_blueprint.route('/api/popular/<string:category>', methods=['GET'])
def get_popular_posts_api(category):
    days = request.args.get('days', 7, type=int)
    limit = request.args.get('limit', 5, type=int)
    
    # 인기 게시글 조회
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = Post.query.filter(Post.created_at >= cutoff_date)
    
    if category != 'all':
        query = query.filter_by(category=category)
    
    posts = query.order_by(Post.views.desc()).limit(limit).all()
    
    # 결과 JSON 변환
    result = [{
        'id': post.id,
        'title': post.title,
        'views': post.views,
        'comment_count': len(post.comments),
        'created_at': post.created_at.strftime('%Y-%m-%d %H:%M'),
        'author': post.user.username
    } for post in posts]
    
    return jsonify(result)