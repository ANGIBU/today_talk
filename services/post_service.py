from models.post import Post
from db import db
from flask_login import current_user
from datetime import datetime, timedelta

def get_all_posts():
    """
    모든 게시글을 가져옵니다.
    """
    return Post.query.order_by(Post.created_at.desc()).all()

def get_post_by_id(post_id):
    """
    특정 게시글을 ID로 가져옵니다.
    """
    return Post.query.get_or_404(post_id)

def create_post(title, content):
    """
    새로운 게시글을 생성합니다.
    """
    new_post = Post(title=title, content=content, user_id=current_user.id)
    db.session.add(new_post)
    db.session.commit()
    return new_post

def update_post(post_id, title, content):
    """
    게시글을 수정합니다.
    """
    post = get_post_by_id(post_id)
    if post.user_id != current_user.id:
        raise PermissionError("수정 권한이 없습니다.")
    
    post.title = title
    post.content = content
    db.session.commit()
    return post

def delete_post(post_id):
    """
    게시글을 삭제합니다.
    """
    post = get_post_by_id(post_id)
    if post.user_id != current_user.id:
        raise PermissionError("삭제 권한이 없습니다.")
    
    db.session.delete(post)
    db.session.commit()
    return post

def get_popular_posts():
    """
    최근 7일간 조회수가 가장 높은 게시글 10개씩 가져옵니다.
    """
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    categories = ["free", "humor", "info"]
    popular_posts = {}

    for category in categories:
        posts = (
            Post.query
            .filter(Post.category == category, Post.created_at >= seven_days_ago)
            .order_by(Post.views.desc())
            .limit(10)
            .all()
        )
        popular_posts[category] = [post.to_dict() for post in posts]

    return popular_posts
