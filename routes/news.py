from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    flash,
    current_app,
    redirect
)
from flask_login import login_required, current_user
from models import db
from models.news import News
from models.comment import Comment  # 댓글을 불러오기 위함
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from sqlalchemy import desc

news_blueprint = Blueprint("news", __name__, url_prefix="/news")

# 네이버 뉴스 카테고리 매핑: key는 문자열 카테고리, value는 해당 뉴스 코드
NAVER_NEWS_CATEGORIES = {
    "politics": "100",
    "economy": "101",
    "domestic": "102",
    "society": "103",
    "world": "104"
}

def scrape_naver_news(category_code):
    """네이버 뉴스 스크래핑 함수 (카테고리별 지원)"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    base_url = f"https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1={category_code}"
    try:
        response = requests.get(base_url, headers=headers)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.select('.cluster_text')  # 기사 목록 선택
        news_list = []
        for article in articles:
            try:
                link_tag = article.select_one('a')
                if not link_tag:
                    continue
                title = link_tag.get_text(strip=True)
                news_url = link_tag['href']
                news_response = requests.get(news_url, headers=headers)
                news_soup = BeautifulSoup(news_response.text, 'html.parser')
                content_tag = news_soup.select_one('#dic_area')
                content = content_tag.get_text(strip=True) if content_tag else "본문 없음"
                press_tag = news_soup.select_one('.press_logo img')
                press = press_tag['title'] if press_tag else "출처 없음"
                date_tag = news_soup.select_one('.media_end_head_info_datestamp_time')
                if date_tag:
                    published_at = datetime.strptime(date_tag.get_text(strip=True), '%Y.%m.%d. %H:%M')
                else:
                    published_at = datetime.now()
                thumbnail_tag = news_soup.select_one('meta[property="og:image"]')
                thumbnail_url = thumbnail_tag['content'] if thumbnail_tag else None
                news_list.append({
                    "title": title,
                    "content": content,
                    "source": press,
                    "source_url": news_url,
                    "thumbnail": thumbnail_url,
                    "published_at": published_at,
                    "category": category_code  # 임시 숫자 코드
                })
            except Exception as e:
                current_app.logger.error(f"Error processing article: {e}")
                continue
        return news_list
    except Exception as e:
        current_app.logger.error(f"Error scraping news: {e}")
        return []

@news_blueprint.route("/update", methods=["GET"], endpoint="update_news")
@login_required
def update_news():
    """네이버 뉴스 스크래핑 실행 및 DB 저장"""
    total_added = 0
    for category, category_code in NAVER_NEWS_CATEGORIES.items():
        news_list = scrape_naver_news(category_code)
        for news_data in news_list:
            news_data["category"] = category  # 숫자 코드 대신 문자열 카테고리로 재설정
            exists = News.query.filter_by(source_url=news_data['source_url']).first()
            if not exists:
                news = News(
                    title=news_data['title'],
                    content=news_data['content'],
                    source=news_data['source'],
                    source_url=news_data['source_url'],
                    thumbnail=news_data['thumbnail'],
                    published_at=news_data['published_at'],
                    category=news_data['category'],
                    user_id=current_user.id
                )
                db.session.add(news)
                total_added += 1
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saving news: {e}")
            flash("뉴스 업데이트 중 오류 발생", "error")
            return redirect(url_for("news.all"))
    flash(f"{total_added}개의 뉴스가 추가되었습니다.", "success")
    return redirect(url_for("news.all"))

def get_news_by_category(category=None, page=1):
    """특정 카테고리 또는 전체 뉴스를 페이지네이션하여 반환"""
    query = News.query
    if category:
        query = query.filter_by(category=category)
    return query.order_by(desc(News.published_at)).paginate(
        page=page, per_page=20, error_out=False
    )

@news_blueprint.route("/all", endpoint="all")
def all_news():
    page = request.args.get("page", 1, type=int)
    news_items = get_news_by_category(page=page)
    return render_template("news/news_all.html", news_items=news_items)

@news_blueprint.route("/world", endpoint="world")
def world_news():
    page = request.args.get("page", 1, type=int)
    news_items = get_news_by_category("world", page)
    return render_template("news/news_world.html", news_items=news_items)

@news_blueprint.route("/politics", endpoint="politics")
def politics_news():
    page = request.args.get("page", 1, type=int)
    news_items = get_news_by_category("politics", page)
    return render_template("news/news_politics.html", news_items=news_items)

@news_blueprint.route("/economy", endpoint="economy")
def economy_news():
    page = request.args.get("page", 1, type=int)
    news_items = get_news_by_category("economy", page)
    return render_template("news/news_economy.html", news_items=news_items)

@news_blueprint.route("/domestic", endpoint="domestic")
def domestic_news():
    page = request.args.get("page", 1, type=int)
    news_items = get_news_by_category("domestic", page)
    return render_template("news/news_domestic.html", news_items=news_items)

@news_blueprint.route("/society", endpoint="society")
def society_news():
    page = request.args.get("page", 1, type=int)
    news_items = get_news_by_category("society", page)
    return render_template("news/news_society.html", news_items=news_items)

@news_blueprint.route("/hot_issues", endpoint="hot_issues")
def hot_issues():
    page = request.args.get("page", 1, type=int)
    news_items = get_news_by_category(page=page)
    return render_template("news/news_hot_issues.html", news_items=news_items)

@news_blueprint.route("/detail/<int:news_id>", endpoint="detail")
def detail_news(news_id):
    news = News.query.get_or_404(news_id)
    # 댓글은 Comment 모델을 사용하여, 해당 뉴스의 ID를 post_id로 조회합니다.
    comments = Comment.query.filter_by(post_id=news_id).order_by(Comment.created_at.asc()).all()
    return render_template("news/news_detail.html", news=news, comments=comments)
