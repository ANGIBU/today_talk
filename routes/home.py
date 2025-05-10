# routes/home.py
from flask import Blueprint, render_template, current_app
from models.post import Post
from models.news import News
from datetime import datetime, timedelta
from sqlalchemy import desc, text
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 블루프린트 정의
home_blueprint = Blueprint('home', __name__, url_prefix='/')

# 메인 페이지
@home_blueprint.route('/')
def index():
    try:
        # 인기 게시글 (최근 7일)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        popular_posts = Post.query.filter(
            Post.created_at >= seven_days_ago
        ).order_by(Post.views.desc()).limit(5).all()
        
        # 최신 뉴스 - 필드 오류 방지를 위한 처리
        try:
            # 기본 컬럼만 선택하여 쿼리
            recent_news = News.query.with_entities(
                News.id, News.title, News.content, News.source, 
                News.thumbnail, News.source_url, News.published_at, 
                News.category, News.views
            ).order_by(
                desc(News.published_at)
            ).limit(5).all()
        except Exception as db_error:
            logger.error(f"뉴스 쿼리 오류, 기본 SQL로 시도: {db_error}")
            # SQLAlchemy Core로 직접 쿼리 실행
            try:
                result = current_app.db.session.execute(text("""
                    SELECT id, title, content, source, thumbnail, source_url, 
                           published_at, category, views 
                    FROM news 
                    ORDER BY published_at DESC 
                    LIMIT 5
                """))
                recent_news = [dict(row) for row in result]
            except Exception as sql_error:
                logger.error(f"SQL 직접 쿼리도 실패: {sql_error}")
                recent_news = []
        
        return render_template(
            'home/index.html',
            popular_posts=popular_posts,
            recent_news=recent_news
        )
    except Exception as e:
        logger.error(f"메인 페이지 로딩 중 오류 발생: {e}")
        return render_template(
            'home/index.html', 
            popular_posts=[], 
            recent_news=[],
            error_message="데이터 로딩 중 문제가 발생했습니다."
        )

# 소개 페이지
@home_blueprint.route('/about')
def about():
    return render_template('home/about.html')

# FAQ 페이지
@home_blueprint.route('/faq')
def faq():
    faqs = [
        {
            'question': '이 사이트는 어떤 사이트인가요?',
            'answer': 'Today Talk은 다양한 주제의 게시글과 뉴스를 한 곳에서 볼 수 있는 커뮤니티 사이트입니다.'
        },
        {
            'question': '게시글 작성은 어떻게 하나요?',
            'answer': '회원가입 후 로그인하시면 게시글을 작성할 수 있습니다. 상단 메뉴에서 원하는 게시판을 선택한 후 [글쓰기] 버튼을 클릭하세요.'
        },
        {
            'question': '비밀번호를 잊어버렸어요.',
            'answer': '로그인 페이지에서 [비밀번호 재설정] 링크를 클릭하여 가입한 이메일로 재설정 링크를 받을 수 있습니다.'
        },
        {
            'question': '게시글이나 댓글을 수정/삭제하고 싶어요.',
            'answer': '본인이 작성한 게시글이나 댓글만 수정/삭제가 가능합니다. 해당 게시글이나 댓글에서 수정/삭제 버튼을 찾을 수 있습니다.'
        },
        {
            'question': '문의사항은 어디로 보내면 되나요?',
            'answer': '사이트 하단의 [문의하기] 링크를 통해 문의 양식을 작성하여 보내주시면 됩니다.'
        }
    ]
    return render_template('home/faq.html', faqs=faqs)

# 이용약관 페이지
@home_blueprint.route('/terms')
def terms():
    return render_template('home/terms.html')

# 개인정보처리방침 페이지
@home_blueprint.route('/privacy')
def privacy():
    return render_template('home/privacy.html')