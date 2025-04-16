from flask import Blueprint, render_template, current_app
from models.post import Post

# Home 블루프린트 정의
home_blueprint = Blueprint('home', __name__, url_prefix='/')

# 메인 페이지 라우트
@home_blueprint.route('/')
def index():
    try:
        posts = Post.query.all()  # 게시글 목록을 가져옵니다.
        return render_template('home/index.html', posts=posts)
    except Exception as e:
        current_app.logger.error(f"Error fetching posts: {e}")
        # 에러 발생 시 빈 게시글 목록과 함께 에러 메시지를 표시합니다.
        return render_template('home/index.html', posts=[], error_message="게시글을 불러오는 중 문제가 발생했습니다.")