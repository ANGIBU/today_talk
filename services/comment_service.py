from models.comment import Comment
from db import db
from flask_login import current_user
from sqlalchemy import case


def get_comment_by_id(comment_id):
    """
    특정 댓글을 ID로 가져옵니다.
    """
    return Comment.query.get_or_404(comment_id)


def create_comment(post_id, content):
    """
    새로운 댓글을 생성합니다.
    """
    new_comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()
    return new_comment


def create_reply(post_id, parent_id, content):
    """
    답글을 생성합니다.
    """
    parent_comment = get_comment_by_id(parent_id)
    reply = Comment(
        content=content,
        user_id=current_user.id,
        post_id=post_id,
        parent_id=parent_id,
        depth=parent_comment.depth + 1,
    )
    db.session.add(reply)
    db.session.commit()
    return reply


def get_comments_for_post(post_id):
    """
    게시글의 모든 댓글을 계층 구조로 가져옵니다.
    """
    return (
        Comment.query.filter_by(post_id=post_id)
        .order_by(case((Comment.parent_id.is_(None), 0), else_=1), Comment.parent_id.asc(), Comment.created_at.asc())
        .all()
    )


def update_comment(comment_id, content):
    """
    댓글을 수정합니다.
    """
    comment = get_comment_by_id(comment_id)
    if comment.user_id != current_user.id:
        raise PermissionError("수정 권한이 없습니다.")

    comment.content = content
    db.session.commit()
    return comment


def delete_comment(comment_id):
    """
    댓글을 삭제합니다.
    """
    comment = get_comment_by_id(comment_id)
    if comment.user_id != current_user.id:
        raise PermissionError("삭제 권한이 없습니다.")

    db.session.delete(comment)
    db.session.commit()
    return comment
