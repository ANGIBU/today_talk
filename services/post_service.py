# services/post_service.py
from models.post import Post
from models.comment import Comment
from db import db
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from flask import current_app
import json

def get_all_posts(page=1, per_page=10, category=None):
    """
    모든 게시글 또는 특정 카테고리의 게시글 조회
    """
    query = Post.query
    
    if category and category != 'all':
        query = query.filter_by(category=category)
        
    return query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

def get_post_by_id(post_id):
    """
    ID로 게시글 조회
    """
    return Post.query.get(post_id)

def create_post(title, content, category, user_id, images=None):
    """
    새 게시글 생성
    """
    try:
        new_post = Post(
            title=title,
            content=content,
            category=category,
            user_id=user_id,
            images=images
        )
        db.session.add(new_post)
        db.session.commit()
        return True, new_post
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def update_post(post_id, title, content, images=None):
    """
    게시글 수정
    """
    post = get_post_by_id(post_id)
    if not post:
        return False, "게시글을 찾을 수 없습니다."
    
    try:
        post.title = title
        post.content = content
        if images is not None:
            post.images = images
        post.updated_at = datetime.utcnow()
        db.session.commit()
        return True, post
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def delete_post(post_id):
    """
    게시글 삭제
    """
    post = get_post_by_id(post_id)
    if not post:
        return False, "게시글을 찾을 수 없습니다."
    
    try:
        # 첨부 이미지 삭제
        if post.images:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            for image in post.images:
                image_path = os.path.join(upload_folder, image)
                if os.path.exists(image_path):
                    os.remove(image_path)
        
        db.session.delete(post)
        db.session.commit()
        return True, "게시글이 성공적으로 삭제되었습니다."
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def increment_view_count(post_id):
    """
    게시글 조회수 증가
    """
    try:
        post = get_post_by_id(post_id)
        if post:
            post.views += 1
            db.session.commit()
            return True
        return False
    except Exception:
        db.session.rollback()
        return False

def get_popular_posts(days=7, limit=5, category=None):
    """
    최근 일정 기간 동안의 인기 게시글 조회
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = Post.query.filter(Post.created_at >= cutoff_date)
    
    if category and category != 'all':
        query = query.filter_by(category=category)
    
    return query.order_by(Post.views.desc()).limit(limit).all()

def get_latest_posts(limit=5, category=None):
    """
    최신 게시글 조회
    """
    query = Post.query
    
    if category and category != 'all':
        query = query.filter_by(category=category)
    
    return query.order_by(Post.created_at.desc()).limit(limit).all()

def save_post_images(files):
    """
    게시글 이미지 저장
    """
    if not files:
        return []
    
    saved_images = []
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    # 업로드 폴더가 없으면 생성
    os.makedirs(upload_folder, exist_ok=True)
    
    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            saved_images.append(unique_filename)
    
    return saved_images

def get_post_categories():
    """
    게시글 카테고리 목록 조회
    """
    return {
        'free': '자유',
        'humor': '유머',
        'info': '정보',
        'popular': '인기',
        'all': '전체'
    }