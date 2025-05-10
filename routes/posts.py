# routes/posts.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort, current_app
from flask_login import login_required, current_user
from models.post import Post
from models.comment import Comment
from models.user import User
from db import db
from sqlalchemy import desc, func, or_
from datetime import datetime

# Blueprint 이름을 posts_blueprint로 변경
posts_blueprint = Blueprint('posts', __name__)

@posts_blueprint.route('/posts/all')
def all_posts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # 최신순 정렬
        posts = Post.query.filter_by(is_deleted=False).order_by(
            desc(Post.created_at)
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('posts/all.html', posts=posts)
    except Exception as e:
        # 로그 기록
        current_app.logger.error(f"포스트 목록 조회 중 오류: {str(e)}")
        return render_template('error.html', error="포스트 목록을 불러오는 중 오류가 발생했습니다."), 500

@posts_blueprint.route('/posts/popular')
def popular_posts():
    try:
        # 인기순(좋아요 기준) 정렬
        posts = Post.query.filter_by(is_deleted=False).order_by(
            desc(Post.likes_count), desc(Post.created_at)
        ).limit(20).all()
        
        return render_template('posts/popular.html', posts=posts)
    except Exception as e:
        current_app.logger.error(f"인기 포스트 목록 조회 중 오류: {str(e)}")
        return render_template('error.html', error="인기 포스트 목록을 불러오는 중 오류가 발생했습니다."), 500

@posts_blueprint.route('/posts/<int:post_id>')
def view_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        
        # 삭제된 게시물인 경우 404 반환
        if post.is_deleted:
            abort(404)
            
        # 조회수 증가 (중복 방지를 위한 세션 체크 로직 생략)
        post.views_count += 1
        db.session.commit()
        
        # 댓글 불러오기
        comments = Comment.query.filter_by(post_id=post_id, is_deleted=False).order_by(Comment.created_at).all()
        
        return render_template('posts/detail.html', post=post, comments=comments)
    except Exception as e:
        current_app.logger.error(f"포스트 상세 조회 중 오류: {str(e)}")
        return render_template('error.html', error="게시물을 불러오는 중 오류가 발생했습니다."), 500

@posts_blueprint.route('/posts/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            
            if not title or not content:
                flash('제목과 내용을 모두 입력해주세요.', 'danger')
                return redirect(url_for('posts.create_post'))
            
            # 새 포스트 생성
            new_post = Post(
                title=title,
                content=content,
                user_id=current_user.id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.session.add(new_post)
            db.session.commit()
            
            flash('게시글이 등록되었습니다.', 'success')
            return redirect(url_for('posts.view_post', post_id=new_post.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"포스트 생성 중 오류: {str(e)}")
            flash('게시글 등록 중 오류가 발생했습니다.', 'danger')
            return redirect(url_for('posts.create_post'))
    
    return render_template('posts/create.html')

@posts_blueprint.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # 작성자 확인
    if post.user_id != current_user.id:
        flash('본인이 작성한 게시글만 수정할 수 있습니다.', 'danger')
        return redirect(url_for('posts.view_post', post_id=post_id))
    
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            
            if not title or not content:
                flash('제목과 내용을 모두 입력해주세요.', 'danger')
                return redirect(url_for('posts.edit_post', post_id=post_id))
            
            # 포스트 수정
            post.title = title
            post.content = content
            post.updated_at = datetime.now()
            
            db.session.commit()
            
            flash('게시글이 수정되었습니다.', 'success')
            return redirect(url_for('posts.view_post', post_id=post_id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"포스트 수정 중 오류: {str(e)}")
            flash('게시글 수정 중 오류가 발생했습니다.', 'danger')
            return redirect(url_for('posts.edit_post', post_id=post_id))
    
    return render_template('posts/edit.html', post=post)

@posts_blueprint.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # 작성자 확인
    if post.user_id != current_user.id:
        flash('본인이 작성한 게시글만 삭제할 수 있습니다.', 'danger')
        return redirect(url_for('posts.view_post', post_id=post_id))
    
    try:
        # 실제로 삭제하지 않고 is_deleted 필드만 True로 설정
        post.is_deleted = True
        post.updated_at = datetime.now()
        
        db.session.commit()
        
        flash('게시글이 삭제되었습니다.', 'success')
        return redirect(url_for('posts.all_posts'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"포스트 삭제 중 오류: {str(e)}")
        flash('게시글 삭제 중 오류가 발생했습니다.', 'danger')
        return redirect(url_for('posts.view_post', post_id=post_id))

# 좋아요 기능
@posts_blueprint.route('/posts/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        
        # 이미 좋아요 눌렀는지 확인하는 로직 필요 (DB 모델에 따라 구현)
        # 여기서는 간단하게 증가만 처리
        post.likes_count += 1
        db.session.commit()
        
        return jsonify({"success": True, "likes_count": post.likes_count})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"포스트 좋아요 처리 중 오류: {str(e)}")
        return jsonify({"success": False, "error": "좋아요 처리 중 오류가 발생했습니다."}), 500

# 검색 기능
@posts_blueprint.route('/posts/search')
def search_posts():
    try:
        keyword = request.args.get('q', '').strip()
        if not keyword:
            return redirect(url_for('posts.all_posts'))
        
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # 제목과 내용에서 검색
        search_results = Post.query.filter(
            Post.is_deleted == False,
            or_(
                Post.title.ilike(f'%{keyword}%'),
                Post.content.ilike(f'%{keyword}%')
            )
        ).order_by(desc(Post.created_at)).paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('posts/search.html', posts=search_results, keyword=keyword)
    except Exception as e:
        current_app.logger.error(f"포스트 검색 중 오류: {str(e)}")
        return render_template('error.html', error="검색 중 오류가 발생했습니다."), 500