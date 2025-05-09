# routes/news.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.news import News
from db import db
from services.news_service import (
    get_news_by_id, get_news_by_category, increment_view_count,
    get_hot_issues, get_related_news, save_news_to_db, scrape_news
)
from datetime import datetime
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 블루프린트 정의
news_blueprint = Blueprint('news', __name__, url_prefix='/news')

# 전체 뉴스 페이지
@news_blueprint.route('/all')
def all():
    page = request.args.get('page', 1, type=int)
    news_items = get_news_by_category(page=page)
    return render_template('news/news_all.html', news_items=news_items)

# 핫이슈 뉴스 페이지
@news_blueprint.route('/hot_issues')
def hot_issues():
    hot_news = get_hot_issues(limit=20)
    return render_template('news/news_hot_issues.html', hot_news=hot_news)

# 정치 뉴스 페이지
@news_blueprint.route('/politics')
def politics():
    page = request.args.get('page', 1, type=int)
    news_items = get_news_by_category('politics', page)
    return render_template('news/news_politics.html', news_items=news_items)

# 경제 뉴스 페이지
@news_blueprint.route('/economy')
def economy():
    page = request.args.get('page', 1, type=int)
    news_items = get_news_by_category('economy', page)
    return render_template('news/news_economy.html', news_items=news_items)

# 국내 뉴스 페이지
@news_blueprint.route('/domestic')
def domestic():
    page = request.args.get('page', 1, type=int)
    news_items = get_news_by_category('domestic', page)
    return render_template('news/news_domestic.html', news_items=news_items)

# 세계 뉴스 페이지
@news_blueprint.route('/world')
def world():
    page = request.args.get('page', 1, type=int)
    news_items = get_news_by_category('world', page)
    return render_template('news/news_world.html', news_items=news_items)

# 뉴스 상세 페이지
@news_blueprint.route('/detail/<int:news_id>')
def detail(news_id):
    news = get_news_by_id(news_id)
    
    if not news:
        flash('존재하지 않는 뉴스입니다.', 'danger')
        return redirect(url_for('news.all'))
    
    # 조회수 증가
    increment_view_count(news_id)
    
    # 관련 뉴스 조회
    related_news = get_related_news(news_id)
    
    return render_template(
        'news/news_detail.html',
        news=news,
        related_news=related_news
    )

# 뉴스 업데이트 기능 (관리자 전용)
@news_blueprint.route('/update', methods=['GET'])
@login_required
def update_news():
    # 권한 확인 (예: 관리자만 접근 가능)
    if not current_user.is_authenticated or current_user.id != 1:  # 관리자 ID 확인
        flash('권한이 없습니다.', 'danger')
        return redirect(url_for('news.all'))
    
    try:
        # 뉴스 스크래핑 실행
        news_items = scrape_news()
        
        if not news_items:
            flash('스크래핑할 뉴스가 없습니다.', 'warning')
            return redirect(url_for('news.all'))
        
        # 스크래핑 결과 DB 저장
        saved_news = save_news_to_db(news_items)
        
        if saved_news:
            flash(f'{len(saved_news)}개의 뉴스가 업데이트되었습니다.', 'success')
        else:
            flash('뉴스 저장 중 오류가 발생했습니다.', 'danger')
        
        return redirect(url_for('news.all'))
        
    except Exception as e:
        logger.error(f"뉴스 업데이트 중 오류 발생: {e}")
        flash('뉴스 업데이트 중 오류가 발생했습니다.', 'danger')
        return redirect(url_for('news.all'))

# 뉴스 API - 카테고리별 최신 뉴스
@news_blueprint.route('/api/<string:category>', methods=['GET'])
def get_news_api(category):
    limit = request.args.get('limit', 5, type=int)
    
    query = News.query
    
    if category != 'all':
        query = query.filter_by(category=category)
    
    news_items = query.order_by(News.published_at.desc()).limit(limit).all()
    
    # 결과 JSON 변환
    result = [{
        'id': news.id,
        'title': news.title,
        'source': news.source,
        'thumbnail': news.thumbnail,
        'published_at': news.published_at.strftime('%Y-%m-%d %H:%M'),
        'category': news.category
    } for news in news_items]
    
    return jsonify(result)

# 뉴스 API - 핫이슈 뉴스
@news_blueprint.route('/api/hot_issues', methods=['GET'])
def get_hot_issues_api():
    limit = request.args.get('limit', 5, type=int)
    
    hot_news = get_hot_issues(limit=limit)
    
    # 결과 JSON 변환
    result = [{
        'id': news.id,
        'title': news.title,
        'source': news.source,
        'thumbnail': news.thumbnail,
        'published_at': news.published_at.strftime('%Y-%m-%d %H:%M'),
        'category': news.category,
        'views': news.views
    } for news in hot_news]
    
    return jsonify(result)