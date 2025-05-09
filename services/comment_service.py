# services/comment_service.py
from models.comment import Comment
from models.post import Post
from db import db
from sqlalchemy import case
from datetime import datetime

def get_comment_by_id(comment_id):
    """
    ID로 댓글 조회
    """
    return Comment.query.get(comment_id)

def get_comments_for_post(post_id):
    """
    게시글의 모든 댓글 조회 (계층 구조)
    """
    return Comment.query.filter_by(post_id=post_id).order_by(
        case((Comment.parent_id.is_(None), 0), else_=1),  # 원댓글 먼저
        Comment.parent_id.asc(),                           # 부모 ID 순서대로
        Comment.created_at.asc()                           # 작성일 오름차순
    ).all()

def create_comment(post_id, user_id, content):
    """
    새 댓글 작성
    """
    try:
        # 게시글 존재 확인
        post = Post.query.get(post_id)
        if not post:
            return False, "게시글을 찾을 수 없습니다."
        
        new_comment = Comment(
            content=content,
            user_id=user_id,
            post_id=post_id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_comment)
        db.session.commit()
        return True, new_comment
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def create_reply(post_id, user_id, parent_id, content):
    """
    답글 작성
    """
    try:
        # 부모 댓글 존재 확인
        parent_comment = get_comment_by_id(parent_id)
        if not parent_comment:
            return False, "원댓글을 찾을 수 없습니다."
        
        # 게시글 일치 확인
        if parent_comment.post_id != post_id:
            return False, "잘못된 게시글입니다."
        
        reply = Comment(
            content=content,
            user_id=user_id,
            post_id=post_id,
            parent_id=parent_id,
            depth=parent_comment.depth + 1,
            created_at=datetime.utcnow()
        )
        
        db.session.add(reply)
        db.session.commit()
        return True, reply
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def update_comment(comment_id, user_id, content):
    """
    댓글 수정
    """
    try:
        comment = get_comment_by_id(comment_id)
        if not comment:
            return False, "댓글을 찾을 수 없습니다."
        
        # 작성자 확인
        if comment.user_id != user_id:
            return False, "수정 권한이 없습니다."
        
        comment.content = content
        comment.updated_at = datetime.utcnow()
        
        db.session.commit()
        return True, comment
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def delete_comment(comment_id, user_id):
    """
    댓글 삭제
    """
    try:
        comment = get_comment_by_id(comment_id)
        if not comment:
            return False, "댓글을 찾을 수 없습니다."
        
        # 작성자 확인
        if comment.user_id != user_id:
            return False, "삭제 권한이 없습니다."
        
        db.session.delete(comment)
        db.session.commit()
        return True, "댓글이 성공적으로 삭제되었습니다."
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def get_recent_comments(limit=5):
    """
    최근 댓글 조회
    """
    return Comment.query.filter_by(parent_id=None).order_by(
        Comment.created_at.desc()
    ).limit(limit).all()

def count_comments(post_id=None):
    """
    댓글 수 조회
    """
    query = Comment.query
    if post_id:
        query = query.filter_by(post_id=post_id)
    return query.count()