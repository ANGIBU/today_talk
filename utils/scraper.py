# utils/scraper.py
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def scrape_naver_news(category='104', page=1):
    """
    네이버 뉴스 스크래핑 함수
    category: 
        - 104: 세계
        - 100: 정치
        - 101: 경제
        - 102: 사회
        - 103: 생활/문화
    """
    try:
        url = f"https://news.naver.com/section/{category}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_list = []
        articles = soup.select('.sa_text_title')
        
        for article in articles:
            try:
                title = article.get_text(strip=True)
                link = article['href']
                
                # 개별 뉴스 페이지 스크래핑
                news_response = requests.get(link, headers=headers)
                news_soup = BeautifulSoup(news_response.text, 'html.parser')
                
                # 언론사
                source = news_soup.select_one('.media_end_head_top img')
                if source:
                    source = source.get('title', '미상')
                else:
                    source = '미상'
                
                # 썸네일 이미지
                thumbnail = news_soup.select_one('meta[property="og:image"]')
                if thumbnail:
                    thumbnail = thumbnail.get('content')
                
                # 본문
                content = news_soup.select_one('#dic_area')
                if content:
                    content = content.get_text(strip=True)
                else:
                    continue
                
                # 작성일
                date_str = news_soup.select_one('.media_end_head_info_datestamp_time')
                if date_str:
                    date_str = date_str.get_text(strip=True)
                    date = datetime.strptime(date_str, '%Y.%m.%d. %H:%M')
                else:
                    date = datetime.now()
                
                news_list.append({
                    'title': title,
                    'content': content,
                    'source': source,
                    'thumbnail': thumbnail,
                    'url': link,
                    'created_at': date
                })
                
            except Exception as e:
                print(f"Error processing article: {e}")
                continue
                
        return news_list
        
    except Exception as e:
        print(f"Error scraping news: {e}")
        return []