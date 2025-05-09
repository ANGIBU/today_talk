# services/news_service.py
from models.news import News
from db import db
from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
from flask import current_app
import random

def get_news_by_id(news_id):
    """특정 뉴스 기사 조회"""
    return News.query.get(news_id)

def get_news_by_category(category=None, page=1, per_page=20):
    """카테고리별 뉴스 기사 목록 조회"""
    query = News.query
    
    if category and category != 'all':
        query = query.filter_by(category=category)
    
    return query.order_by(News.published_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

def increment_view_count(news_id):
    """뉴스 조회수 증가"""
    try:
        news = get_news_by_id(news_id)
        if news:
            news.views += 1
            db.session.commit()
            return True
        return False
    except Exception:
        db.session.rollback()
        return False

def get_hot_issues(limit=10):
    """인기 뉴스 기사 조회"""
    return News.query.order_by(News.views.desc()).limit(limit).all()

def get_related_news(news_id, limit=5):
    """관련 뉴스 기사 조회"""
    news = get_news_by_id(news_id)
    if not news:
        return []
    
    # 같은 카테고리의 다른 뉴스 기사 중에서 관련 기사 조회
    return News.query.filter(
        News.category == news.category,
        News.id != news.id
    ).order_by(News.published_at.desc()).limit(limit).all()

def save_news_to_db(news_list):
    """스크래핑한 뉴스 DB에 저장"""
    if not news_list:
        current_app.logger.info("저장할 뉴스가 없습니다.")
        return []
    
    saved_news = []
    
    for news_data in news_list:
        # 중복 뉴스 확인 (URL 기준)
        existing_news = News.query.filter_by(source_url=news_data.get('source_url')).first()
        if existing_news:
            continue
        
        try:
            news = News(
                title=news_data.get('title', '제목 없음'),
                content=news_data.get('content', '내용 없음'),
                source=news_data.get('source', '출처 없음'),
                thumbnail=news_data.get('thumbnail'),
                source_url=news_data.get('source_url'),
                published_at=news_data.get('published_at', datetime.utcnow()),
                category=news_data.get('category', 'general'),
                images=news_data.get('images'),
                author=news_data.get('author'),
                author_email=news_data.get('author_email'),
                user_id=news_data.get('user_id', 1)  # 기본 관리자 ID
            )
            
            db.session.add(news)
            saved_news.append(news)
        except Exception as e:
            current_app.logger.error(f"뉴스 저장 중 오류 발생: {e}")
    
    try:
        db.session.commit()
        return saved_news
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"뉴스 일괄 저장 중 오류 발생: {e}")
        return []

def scrape_news():
    """뉴스 스크래핑 함수 (샘플)"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 네이버 뉴스 메인 페이지에서 뉴스 스크래핑
        url = "https://news.naver.com/"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_items = []
        articles = soup.select('.section_headline .sh_text')
        
        for idx, article in enumerate(articles[:10]):  # 최대 10개 기사만 스크래핑
            try:
                title_tag = article.select_one('.sh_text_headline')
                link_tag = title_tag
                
                if not title_tag or not link_tag:
                    continue
                
                title = title_tag.text.strip()
                link = link_tag['href']
                
                # 기사 상세 페이지 스크래핑
                article_response = requests.get(link, headers=headers)
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # 언론사
                press_tag = article_soup.select_one('.media_end_head_top img')
                press = press_tag.get('title', '출처 없음') if press_tag else '출처 없음'
                
                # 본문
                content_tag = article_soup.select_one('#dic_area')
                content = content_tag.text.strip() if content_tag else '내용 없음'
                
                # 작성자
                author_tag = article_soup.select_one('.media_end_head_journalist_name')
                author = author_tag.text.strip() if author_tag else None
                
                # 썸네일
                thumbnail_tag = article_soup.select_one('meta[property="og:image"]')
                thumbnail = thumbnail_tag['content'] if thumbnail_tag else None
                
                # 카테고리 (기사 상세 페이지에서 추출)
                category_tag = article_soup.select_one('.media_end_categorize_item')
                category_text = category_tag.text.strip() if category_tag else '일반'
                
                # 카테고리 매핑 (한글 -> 영어)
                category_map = {
                    '정치': 'politics',
                    '경제': 'economy',
                    '사회': 'domestic',
                    '생활/문화': 'culture',
                    '세계': 'world',
                    '과학': 'science',
                    'IT/과학': 'science',
                    '연예': 'entertainment',
                    '스포츠': 'sports'
                }
                
                category = category_map.get(category_text, 'general')
                
                # 발행일
                date_tag = article_soup.select_one('.media_end_head_info_datestamp_time')
                if date_tag and date_tag.get('data-date-time'):
                    published_at = datetime.fromisoformat(date_tag['data-date-time'].replace('Z', '+00:00'))
                else:
                    published_at = datetime.utcnow()
                
                # 이미지 추출
                images = []
                image_tags = article_soup.select('#dic_area img')
                for img in image_tags:
                    if img.get('src'):
                        images.append({
                            'url': img['src'],
                            'alt': img.get('alt', ''),
                            'caption': img.find_next('em', class_='img_desc').text.strip() if img.find_next('em', class_='img_desc') else None
                        })
                
                news_items.append({
                    'title': title,
                    'content': content,
                    'source': press,
                    'source_url': link,
                    'thumbnail': thumbnail,
                    'category': category,
                    'published_at': published_at,
                    'author': author,
                    'images': images,
                    'user_id': 1  # 관리자 ID
                })
                
            except Exception as e:
                current_app.logger.error(f"기사 스크래핑 중 오류 발생: {e}")
        
        return news_items
        
    except Exception as e:
        current_app.logger.error(f"뉴스 스크래핑 중 오류 발생: {e}")
        return []

def get_news_categories():
    """뉴스 카테고리 목록 조회"""
    return {
        'politics': '정치',
        'economy': '경제',
        'domestic': '국내',
        'world': '세계',
        'society': '사회',
        'culture': '문화',
        'science': '과학',
        'entertainment': '연예',
        'sports': '스포츠',
        'hot_issues': '핫이슈',
        'all': '전체'
    }