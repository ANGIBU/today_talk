# routes/comments.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.comment import Comment
from models.post import Post
from db import db
from services.comment_service import (
    get_comment_by_id, create_comment, create_reply,
    update_comment, delete_comment
)
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 블루프린트 정의
comments_blueprint = Blueprint('comments', __name__, url_prefix='/comments')

# 댓글 작성
@comments_blueprint.route('/<int:post_id>/create', methods=['POST'])
@login_required
def create_comment_route(post_id):
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('댓글 내용을 입력해주세요.', 'danger')
        return redirect(url_for('posts.detail_post', post_id=post_id))
    
    # 댓글 생성
    success, result = create_comment(
        post_id=post_id,
        user_id=current_user.id,
        content=content
    )
    
    if success:
        flash('댓글이 성공적으로 작성되었습니다.', 'success')
    else:
        flash(f'댓글 작성 중 오류가 발생했습니다: {result}', 'danger')
    
    return redirect(url_for('posts.detail_post', post_id=post_id))

# 답글 작성
@comments_blueprint.route('/<int:post_id>/<int:parent_id>/reply', methods=['POST'])
@login_required
def create_reply_route(post_id, parent_id):
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('답글 내용을 입력해주세요.', 'danger')
        return redirect(url_for('posts.detail_post', post_id=post_id))
    
    # 답글 생성
    success, result = create_reply(
        post_id=post_id,
        user_id=current_user.id,
        parent_id=parent_id,
        content=content
    )
    
    if success:
        flash('답글이 성공적으로 작성되었습니다.', 'success')
    else:
        flash(f'답글 작성 중 오류가 발생했습니다: {result}', 'danger')
    
    return redirect(url_for('posts.detail_post', post_id=post_id))

# 댓글 수정 페이지
@comments_blueprint.route('/<int:comment_id>/edit', methods=['GET'])
@login_required
def edit_comment_route(comment_id):
    comment = get_comment_by_id(comment_id)
    
    if not comment:
        flash('존재하지 않는 댓글입니다.', 'danger')
        return redirect(url_for('home.index'))
    
    # 작성자 권한 확인
    if comment.user_id != current_user.id:
        flash('수정 권한이 없습니다.', 'danger')
        return redirect(url_for('posts.detail_post', post_id=comment.post_id))
    
    return render_template('comments/edit.html', comment=comment)

# 댓글 수정 처리
@comments_blueprint.route('/<int:comment_id>/edit', methods=['POST'])
@login_required
def update_comment_route(comment_id):
    comment = get_comment_by_id(comment_id)
    
    if not comment:
        flash('존재하지 않는 댓글입니다.', 'danger')
        return redirect(url_for('home.index'))
    
    # 작성자 권한 확인
    if comment.user_id != current_user.id:
        flash('수정 권한이 없습니다.', 'danger')
        return redirect(url_for('posts.detail_post', post_id=comment.post_id))
    
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('댓글 내용을 입력해주세요.', 'danger')
        return redirect(url_for('comments.edit_comment_route', comment_id=comment_id))
    
    # 댓글 수정
    success, result = update_comment(
        comment_id=comment_id,
        user_id=current_user.id,
        content=content
    )
    
    if success:
        flash('댓글이 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('posts.detail_post', post_id=comment.post_id))
    else:
        flash(f'댓글 수정 중 오류가 발생했습니다: {result}', 'danger')
        return redirect(url_for('comments.edit_comment_route', comment_id=comment_id))

# 댓글 삭제 처리
@comments_blueprint.route('/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment_route(comment_id):
    comment = get_comment_by_id(comment_id)
    
    if not comment:
        flash('존재하지 않는 댓글입니다.', 'danger')
        return redirect(url_for('home.index'))
    
    # 작성자 권한 확인
    if comment.user_id != current_user.id:
        flash('삭제 권한이 없습니다.', 'danger')
        return redirect(url_for('posts.detail_post', post_id=comment.post_id))
    
    post_id = comment.post_id
    
    # 댓글 삭제
    success, message = delete_comment(
        comment_id=comment_id,
        user_id=current_user.id
    )
    
    if success:
        flash('댓글이 성공적으로 삭제되었습니다.', 'success')
    else:
        flash(f'댓글 삭제 중 오류가 발생했습니다: {message}', 'danger')
    
    return redirect(url_for('posts.detail_post', post_id=post_id))

# 댓글 API - 최근 댓글 목록
@comments_blueprint.route('/api/recent', methods=['GET'])
def get_recent_comments_api():
    limit = request.args.get('limit', 5, type=int)
    
    comments = Comment.query.filter_by(parent_id=None).order_by(
        Comment.created_at.desc()
    ).limit(limit).all()
    
    # 결과 JSON 변환
    result = [{
        'id': comment.id,
        'content': comment.content[:50] + '...' if len(comment.content) > 50 else comment.content,
        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
        'post_id': comment.post_id,
        'author': comment.user.username if comment.user else '알 수 없음',
        'post_title': comment.post.title if comment.post else '알 수 없음'
    } for comment in comments]
    
    return jsonify(result)