# routes/news.py
from flask import Blueprint, render_template, request, redirect, url_for, abort, jsonify, current_app
from models.news import News
from db import db
from sqlalchemy import desc, func, text
from datetime import datetime, timedelta

news_blueprint = Blueprint('news', __name__, url_prefix='/news')

@news_blueprint.route('/all')
def all():
    """전체 뉴스 목록 표시"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 삭제되지 않은 최신 뉴스 가져오기
    news_items = News.query.filter_by(is_deleted=False).order_by(
        desc(News.published_at)
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('news/news_all.html', news_items=news_items)

@news_blueprint.route('/politics')
def politics():
    """정치 뉴스 목록 표시"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    news_items = News.query.filter_by(
        category='politics',
        is_deleted=False
    ).order_by(desc(News.published_at)).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('news/news_politics.html', news_items=news_items)

@news_blueprint.route('/economy')
def economy():
    """경제 뉴스 목록 표시"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    news_items = News.query.filter_by(
        category='economy',
        is_deleted=False
    ).order_by(desc(News.published_at)).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('news/news_economy.html', news_items=news_items)

@news_blueprint.route('/domestic')
def domestic():
    """국내 뉴스 목록 표시"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    news_items = News.query.filter_by(
        category='domestic',
        is_deleted=False
    ).order_by(desc(News.published_at)).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('news/news_domestic.html', news_items=news_items)

@news_blueprint.route('/world')
def world():
    """세계 뉴스 목록 표시"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    news_items = News.query.filter_by(
        category='world',
        is_deleted=False
    ).order_by(desc(News.published_at)).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('news/news_world.html', news_items=news_items)

@news_blueprint.route('/detail/<int:news_id>')
def detail(news_id):
    """뉴스 상세 페이지 표시"""
    news = News.query.get_or_404(news_id)
    
    if news.is_deleted:
        abort(404)
    
    # 조회수 증가
    news.views += 1
    db.session.commit()
    
    # 관련 뉴스 - 같은 카테고리의 최신 뉴스 4개 (현재 뉴스 제외)
    related_news = News.query.filter(
        News.category == news.category,
        News.id != news.id,
        News.is_deleted == False
    ).order_by(desc(News.published_at)).limit(4).all()
    
    return render_template('news/news_detail.html', news=news, related_news=related_news)

@news_blueprint.route('/search')
def search():
    """뉴스 검색 결과 표시"""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    if not query:
        return redirect(url_for('news.all'))
    
    # 제목이나 내용에서 검색
    search_results = News.query.filter(
        News.is_deleted == False,
        (News.title.ilike(f'%{query}%') | News.content.ilike(f'%{query}%'))
    ).order_by(desc(News.published_at)).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('news/news_search.html', news_items=search_results, query=query)

@news_blueprint.route('/hot-issues')
def hot_issues():
    """인기 뉴스 목록 표시"""
    # 최근 7일 내 조회수 상위 뉴스
    one_week_ago = datetime.now() - timedelta(days=7)
    
    hot_news = News.query.filter(
        News.is_deleted == False,
        News.published_at >= one_week_ago
    ).order_by(desc(News.views), desc(News.published_at)).limit(10).all()
    
    return render_template('news/news_hot_issues.html', news_items=hot_news)

@news_blueprint.route('/api/recent', methods=['GET'])
def api_recent():
    """최신 뉴스 API (JSON)"""
    limit = request.args.get('limit', 5, type=int)
    category = request.args.get('category', None)
    
    query = News.query.filter_by(is_deleted=False)
    
    if category:
        query = query.filter_by(category=category)
    
    recent_news = query.order_by(desc(News.published_at)).limit(limit).all()
    
    return jsonify({
        'success': True,
        'data': [news.to_dict() for news in recent_news]
    })