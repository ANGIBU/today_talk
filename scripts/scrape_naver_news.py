# scripts/scrape_naver_news.py
import requests
import time
import random
import logging
import os
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from db import db
from models.news import News
from scripts.image_utils import download_image

# 로깅 설정
logger = logging.getLogger('news_scraper')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# 네이버 뉴스 카테고리 URL
NAVER_NEWS_CATEGORIES = {
    'politics': 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=100',
    'economy': 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=101',
    'domestic': 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=102',
    'world': 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=104',
    'tech': 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=105',
}

# 리퀘스트 헤더 설정
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

def get_article_id_from_url(url):
    """URL에서
    기사 ID를 추출합니다."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # 네이버 뉴스 URL 형식에 따라 다양한 파라미터에서 ID 추출 시도
    article_id = None
    for param in ['aid', 'articleId', 'news_id']:
        if param in query_params:
            article_id = query_params[param][0]
            break
    
    # ID를 찾지 못한 경우 URL 패턴을 확인하여 추출 시도
    if not article_id and '/article/' in url:
        # URL 패턴: https://n.news.naver.com/mnews/article/XXX/YYYYYYY 형식 처리
        parts = url.split('/article/')
        if len(parts) > 1 and '/' in parts[1]:
            try:
                article_id = parts[1].split('/')[1]
            except (IndexError, ValueError):
                pass
    
    return article_id

def extract_publisher(soup):
    """기사 언론사 추출"""
    try:
        # 다양한 방식으로 언론사명 추출 시도
        publisher_candidates = [
            soup.select_one('.press_logo img'),
            soup.select_one('.c_inner .c_company'),
            soup.select_one('.press_logo'),
            soup.select_one('.media_end_head_top_logo img'),
            soup.select_one('.media_end_head_top_logo'),
            soup.select_one('.article_header .press'),
            soup.select_one('meta[property="og:site_name"]')
        ]
        
        for candidate in publisher_candidates:
            if candidate:
                if candidate.name == 'meta':
                    return candidate.get('content')
                elif candidate.name == 'img':
                    return candidate.get('alt') or candidate.get('title')
                else:
                    return candidate.get_text(strip=True)
        
        return None
    except Exception:
        return None

def extract_author(soup):
    """기사 작성자 추출"""
    try:
        author_candidates = [
            soup.select_one('.byline_s'),
            soup.select_one('.article_footer .author'),
            soup.select_one('.reporter_area'),
            soup.select_one('.journalistcard_summary_name'),
            soup.select_one('.byline')
        ]
        
        for candidate in author_candidates:
            if candidate:
                return candidate.get_text(strip=True)
        
        return None
    except Exception:
        return None

def extract_article_content(url, max_retries=3):
    """
    뉴스 기사의 내용을 추출합니다.
    
    Args:
        url (str): 뉴스 기사 URL
        max_retries (int): 최대 재시도 횟수
        
    Returns:
        tuple: (제목, 내용, 이미지URL, 언론사, 작성자) 튜플 또는 실패 시 (None, None, None, None, None)
    """
    retries = 0
    while retries < max_retries:
        try:
            # 요청 사이에 랜덤 딜레이 추가 (봇 감지 방지)
            time.sleep(random.uniform(1.0, 3.0))
            
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 다양한 네이버 뉴스 템플릿 지원
            title = None
            content = None
            main_img_url = None
            publisher = None
            author = None
            
            # 제목 추출 시도
            title_candidates = [
                soup.select_one('h2.media_end_head_headline'),
                soup.select_one('h2.end_tit'),
                soup.select_one('h3.tts_head'),
                soup.select_one('h3.article_title'),
                soup.select_one('h2.news_title'),
                soup.select_one('h1.title'),
                soup.select_one('meta[property="og:title"]')
            ]
            
            for candidate in title_candidates:
                if candidate:
                    if candidate.name == 'meta':
                        title = candidate.get('content')
                    else:
                        title = candidate.get_text(strip=True)
                    break
            
            # 내용 추출 시도
            content_candidates = [
                soup.select_one('div#newsct_article'),
                soup.select_one('div#articeBody'),
                soup.select_one('div.article_body'),
                soup.select_one('div.news_end_content'),
                soup.select_one('div#articleBodyContents'),
                soup.select_one('div.article_content'),
                soup.select_one('div.content_area'),
                soup.select_one('div.article_area')
            ]
            
            for candidate in content_candidates:
                if candidate:
                    # 불필요한 요소 제거
                    for tag in candidate.select('.reference, .media_end_sponsorship, .byline, .reporter_area, script, style'):
                        if tag:
                            tag.decompose()
                    
                    content = candidate.get_text(strip=True).replace('\n', ' ').replace('\t', ' ')
                    
                    # 중복 공백 제거
                    while '  ' in content:
                        content = content.replace('  ', ' ')
                    break
            
            # 이미지 URL 추출 시도
            img_candidates = [
                soup.select_one('.end_photo_org img'),
                soup.select_one('.news_media_img img'),
                soup.select_one('.article_photo img'),
                soup.select_one('.news_picture img'),
                soup.select_one('.article_img img'),
                soup.select_one('.article_main_img img'),
                soup.select_one('meta[property="og:image"]'),  # OG 이미지 태그 추가
                soup.select_one('meta[name="twitter:image"]')  # Twitter 이미지 태그 추가
            ]
            
            for candidate in img_candidates:
                if candidate:
                    # meta 태그인 경우 content 속성 사용
                    if candidate.name == 'meta':
                        main_img_url = candidate.get('content')
                    else:
                        main_img_url = candidate.get('src')
                        
                    if main_img_url:
                        # 상대 경로인 경우 절대 경로로 변환
                        if main_img_url.startswith('//'):
                            main_img_url = 'https:' + main_img_url
                        break
            
            # 언론사 및 작성자 추출
            publisher = extract_publisher(soup)
            author = extract_author(soup)
            
            # 필수 정보 확인
            if not title or not content:
                raise ValueError("제목 또는 내용을 찾을 수 없습니다")
                
            # 내용이 너무 짧은 경우 예외 처리
            if len(content) < 50:
                raise ValueError("기사 내용이 너무 짧습니다 (50자 미만)")
                
            return title, content, main_img_url, publisher, author
            
        except Exception as e:
            retries += 1
            logger.error(f"기사 내용 추출 중 오류 발생: {str(e)} - URL: {url}")
            
            # 마지막 시도에서 실패한 경우
            if retries >= max_retries:
                logger.error(f"최대 재시도 횟수 초과. 기사 스크래핑 실패: {url}")
                return None, None, None, None, None
                
    return None, None, None, None, None

def scrape_naver_news(category_url, category_name, limit=20, app=None):
    """
    네이버 뉴스 카테고리 페이지에서 기사를 스크래핑하고 데이터베이스에 저장합니다.
    
    Args:
        category_url (str): 스크래핑할 카테고리 URL
        category_name (str): 카테고리 이름 (예: politics, economy 등)
        limit (int): 수집할 최대 기사 수
        app (Flask): Flask 애플리케이션 객체 (이미지 저장 경로 설정용)
        
    Returns:
        int: 성공적으로 스크래핑한 기사 수
    """
    logger.info(f"[{category_name}] 뉴스 스크래핑 시작")
    
    try:
        # 업로드 폴더 설정
        upload_folder = 'static/uploads/news'
        if app:
            upload_folder = os.path.join(app.static_folder, 'uploads/news')
        
        # 1. 카테고리 페이지 요청
        response = requests.get(category_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # 2. 기사 링크 추출
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 다양한 네이버 뉴스 레이아웃에 대응
        article_links = []
        
        # 메인 헤드라인 링크
        headlines = soup.select('.headline_cluster a.cjs_news_a, .cluster_text a.cjs_news_a')
        for link in headlines:
            href = link.get('href')
            if href and 'news.naver.com' in href:
                article_links.append(href)
        
        # 일반 기사 링크
        news_links = soup.select('.cluster_item a.cjs_news_a, .cjs_ct_hab a.cjs_news_a')
        for link in news_links:
            href = link.get('href')
            if href and 'news.naver.com' in href:
                article_links.append(href)
                
        # 추가 링크 형식 지원
        more_links = soup.select('.cjs_news_list a.cjs_news_a, .section_latest a.cjs_news_a')
        for link in more_links:
            href = link.get('href')
            if href and 'news.naver.com' in href:
                article_links.append(href)
        
        # 중복 제거 및 제한
        article_links = list(dict.fromkeys(article_links))[:limit]
        
        if not article_links:
            logger.warning(f"[{category_name}] 기사 링크를 찾을 수 없습니다.")
            return 0
        
        # 3. 각 기사 내용 추출 및 저장
        success_count = 0
        for i, url in enumerate(article_links):
            logger.info(f"[{category_name}] {i+1}/{len(article_links)} 기사 처리 중: {url}")
            
            # 이미 저장된 기사인지 확인
            article_id = get_article_id_from_url(url)
            if article_id:
                existing_news = News.query.filter_by(source_id=article_id).first()
                if existing_news:
                    logger.info(f"이미 저장된 기사입니다: {url}")
                    continue
            
            # 기사 내용 추출
            title, content, image_url, publisher, author = extract_article_content(url)
            
            if title and content:
                try:
                    # 이미지 다운로드 및 썸네일 생성
                    image_path = None
                    thumbnail_path = None
                    
                    if image_url:
                        image_path, thumbnail_path = download_image(
                            image_url, 
                            upload_folder, 
                            max_size=(800, 800), 
                            thumb_size=(300, 200)
                        )
                        
                        if image_path and not image_path.startswith('/'):
                            image_path = '/' + image_path
                            
                        if thumbnail_path and not thumbnail_path.startswith('/'):
                            thumbnail_path = '/' + thumbnail_path
                            
                        # thumbnail 필드 (기존 필드)에도 저장
                        thumbnail = thumbnail_path
                    
                    # 새 기사 객체 생성 및 저장
                    news = News(
                        title=title,
                        content=content[:10000],  # 내용이 너무 길면 자름
                        source=publisher,  # 언론사 정보 추가
                        author=author,  # 작성자 정보 추가
                        image_url=image_url,
                        image_path=image_path,
                        thumbnail_path=thumbnail_path,
                        thumbnail=thumbnail_path,  # 기존 필드 지원
                        source_url=url,
                        source_id=article_id or '',
                        category=category_name,
                        published_at=datetime.now(),
                        views=0,  # 조회수 초기화
                        user_id=1  # 임시 사용자 ID (필요에 따라 수정)
                    )
                    
                    db.session.add(news)
                    db.session.commit()
                    
                    logger.info(f"기사 스크래핑 성공: {title}")
                    success_count += 1
                    
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"기사 저장 중 오류 발생: {str(e)}")
            
            # 크롤링 간격 조절 (봇 감지 방지)
            time.sleep(random.uniform(1.0, 3.0))
        
        logger.info(f"[{category_name}] 뉴스 스크래핑 완료. 총 {success_count}개 기사 수집.")
        return success_count
        
    except Exception as e:
        logger.error(f"[{category_name}] 카테고리 스크래핑 중 오류 발생: {str(e)}")
        return 0

if __name__ == "__main__":
    # 테스트를 위한 단독 실행 코드
    from flask import Flask
    from db import db
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        db.init_app(app)
        db.create_all()
        
        for category, url in NAVER_NEWS_CATEGORIES.items():
            print(f"카테고리 '{category}' 스크래핑 시작...")
            count = scrape_naver_news(url, category, limit=5, app=app)
            print(f"카테고리 '{category}' 스크래핑 완료. {count}개 기사 수집.")