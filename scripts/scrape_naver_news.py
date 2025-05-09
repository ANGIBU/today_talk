# scripts/scrape_naver_news.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
import logging
import json
import sys
import os

# Flask 애플리케이션 경로 추가 (파일을 직접 실행할 때 필요)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 애플리케이션 모듈 임포트
try:
    from db import db
    from models.news import News
except ImportError:
    print("모듈 임포트 오류. 애플리케이션 구조를 확인해주세요.")
    sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraping.log')
    ]
)
logger = logging.getLogger('news_scraper')

# 네이버 뉴스 카테고리별 URL
NAVER_NEWS_CATEGORIES = {
    'politics': 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=100',  # 정치
    'economy': 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=101',   # 경제
    'domestic': 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=102',  # 사회
    'world': 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=104',     # 세계
}

# HTTP 요청 헤더
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

def get_article_content(url, max_retries=3):
    """
    뉴스 기사 상세 내용 스크래핑
    
    Args:
        url (str): 기사 URL
        max_retries (int): 최대 재시도 횟수
        
    Returns:
        dict: 기사 상세 정보 딕셔너리
    """
    # URL 정규화
    if url.startswith("//"):
        url = f"https:{url}"
    
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                logger.warning(f"기사 접근 실패: {url} (상태 코드: {response.status_code})")
                retries += 1
                time.sleep(random.uniform(1, 3))
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. 기본 정보 추출
            title_tag = soup.select_one('#title_area span') or soup.select_one('h2.media_end_head_headline')
            title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
            
            # 2. 언론사
            source_tag = soup.select_one('.media_end_head_top img') or soup.select_one('.press_logo img')
            source = source_tag.get('title', '출처 없음') if source_tag else '출처 없음'
            
            # 3. 작성 시간
            date_tag = soup.select_one('.media_end_head_info_datestamp_time')
            if date_tag and date_tag.get('data-date-time'):
                try:
                    published_at = datetime.fromisoformat(date_tag.get('data-date-time').replace('Z', '+00:00'))
                except ValueError:
                    published_at = datetime.now()
            else:
                published_at = datetime.now()
            
            # 4. 작성자 정보
            author_tag = soup.select_one('.media_end_head_journalist_name')
            author = author_tag.get_text(strip=True) if author_tag else None
            
            author_email_tag = soup.select_one('.media_end_head_journalist_email')
            author_email = author_email_tag.get_text(strip=True) if author_email_tag else None
            
            # 5. 본문 내용
            content_area = soup.select_one('#dic_area') or soup.select_one('.news_end_content')
            if not content_area:
                logger.warning(f"기사 본문을 찾을 수 없음: {url}")
                retries += 1
                time.sleep(random.uniform(1, 3))
                continue
            
            # 본문 텍스트 추출
            content = content_area.get_text(strip=True, separator='\n')
            
            # 6. 이미지 정보
            images = []
            for img in content_area.select('img'):
                if img.get('data-src'):
                    img_url = img.get('data-src')
                elif img.get('src'):
                    img_url = img.get('src')
                else:
                    continue
                
                if img_url.startswith('//'):
                    img_url = f'https:{img_url}'
                
                # 이미지 캡션
                caption_tag = img.find_next('em', class_='img_desc') or img.find_parent('figure').find('figcaption')
                caption = caption_tag.get_text(strip=True) if caption_tag else None
                
                images.append({
                    'url': img_url,
                    'alt': img.get('alt', ''),
                    'caption': caption
                })
            
            # 7. 썸네일 (메타 태그에서 추출)
            thumbnail_tag = soup.select_one('meta[property="og:image"]')
            thumbnail = thumbnail_tag.get('content') if thumbnail_tag else None
            
            # 8. 원문 URL
            source_url_tag = soup.select_one('a.media_end_head_origin_link')
            source_url = source_url_tag.get('href') if source_url_tag else url
            
            result = {
                'title': title,
                'content': content,
                'published_at': published_at,
                'source': source,
                'source_url': source_url,
                'thumbnail': thumbnail,
                'images': images,
                'author': author,
                'author_email': author_email
            }
            
            logger.info(f"기사 스크래핑 성공: {title}")
            return result
            
        except Exception as e:
            logger.error(f"기사 내용 추출 중 오류 발생: {e} - URL: {url}")
            retries += 1
            time.sleep(random.uniform(1, 3))
    
    logger.error(f"최대 재시도 횟수 초과. 기사 스크래핑 실패: {url}")
    return None

def scrape_naver_news(category_url, category_name, limit=20):
    """
    네이버 뉴스 카테고리별 스크래핑
    
    Args:
        category_url (str): 카테고리 URL
        category_name (str): 카테고리 이름 (영문)
        limit (int): 스크래핑할 기사 수 제한
        
    Returns:
        list: 스크래핑한 뉴스 기사 목록
    """
    logger.info(f"[{category_name}] 뉴스 스크래핑 시작")
    news_list = []
    
    try:
        # 카테고리 페이지 요청
        response = requests.get(category_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            logger.error(f"카테고리 페이지 접근 실패: {category_url} (상태 코드: {response.status_code})")
            return news_list
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 기사 링크 추출 (섹션 헤드라인, 주요 뉴스, 최신 뉴스)
        article_links = set()
        for article in soup.select('.sa_item'):
            link_tag = article.select_one('a.sa_text_title')
            if link_tag and link_tag.get('href'):
                article_links.add(link_tag.get('href'))
                
                # 제한된 기사 수에 도달하면 중단
                if len(article_links) >= limit:
                    break
        
        # 각 기사 상세 페이지 스크래핑
        for idx, link in enumerate(list(article_links)[:limit]):
            logger.info(f"[{category_name}] {idx+1}/{len(article_links)} 기사 처리 중: {link}")
            
            # 요청 간 간격 두기 (서버 부하 방지)
            time.sleep(random.uniform(0.5, 1.5))
            
            article_data = get_article_content(link)
            if article_data:
                article_data['category'] = category_name
                news_list.append(article_data)
        
        logger.info(f"[{category_name}] 뉴스 스크래핑 완료. 총 {len(news_list)}개 기사 수집.")
        return news_list
        
    except Exception as e:
        logger.error(f"[{category_name}] 뉴스 스크래핑 중 오류 발생: {e}")
        return news_list

def save_to_database(news_list, app):
    """
    스크래핑한 뉴스를 데이터베이스에 저장
    
    Args:
        news_list (list): 뉴스 기사 목록
        app: Flask 애플리케이션 컨텍스트
        
    Returns:
        int: 저장된 기사 수
    """
    if not news_list:
        logger.info("저장할 뉴스가 없습니다.")
        return 0
    
    saved_count = 0
    
    with app.app_context():
        for news_data in news_list:
            try:
                # 중복 확인 (URL 기준)
                existing = News.query.filter_by(source_url=news_data['source_url']).first()
                if existing:
                    logger.info(f"중복 기사 건너뛰기: {news_data['title']}")
                    continue
                
                # 이미지 정보 직렬화
                images_json = json.dumps(news_data['images']) if news_data['images'] else None
                
                # 새 뉴스 기사 생성
                news = News(
                    title=news_data['title'],
                    content=news_data['content'],
                    source=news_data['source'],
                    thumbnail=news_data['thumbnail'],
                    source_url=news_data['source_url'],
                    published_at=news_data['published_at'],
                    category=news_data['category'],
                    images=images_json,
                    author=news_data['author'],
                    author_email=news_data['author_email'],
                    created_at=datetime.now(),
                    user_id=1  # 기본 관리자 ID
                )
                
                db.session.add(news)
                saved_count += 1
                
                # 10개마다 커밋 (메모리 사용량 관리)
                if saved_count % 10 == 0:
                    db.session.commit()
                    logger.info(f"{saved_count}개 기사 저장 완료")
                
            except Exception as e:
                logger.error(f"기사 저장 중 오류 발생: {e} - {news_data['title']}")
                db.session.rollback()
        
        # 최종 커밋
        try:
            db.session.commit()
            logger.info(f"총 {saved_count}개 기사 저장 완료")
        except Exception as e:
            logger.error(f"최종 커밋 중 오류 발생: {e}")
            db.session.rollback()
            
    return saved_count

def main():
    """메인 스크래핑 함수"""
    # Flask 애플리케이션 컨텍스트 가져오기
    from app import create_app
    app = create_app()
    
    all_news = []
    
    # 각 카테고리별 스크래핑
    for category_name, category_url in NAVER_NEWS_CATEGORIES.items():
        logger.info(f"===== {category_name} 카테고리 스크래핑 시작 =====")
        category_news = scrape_naver_news(category_url, category_name, limit=20)
        all_news.extend(category_news)
        
        # 카테고리 간 간격 두기
        time.sleep(random.uniform(2, 5))
    
    # 수집한 뉴스 DB 저장
    if all_news:
        save_to_database(all_news, app)
    
    logger.info("스크래핑 작업 완료!")

if __name__ == "__main__":
    main()