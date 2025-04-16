# services/scraping.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from models.news import News
from db import db  # Flask 애플리케이션과 DB 연결

def scrape_naver_hot_issues():
    url = "https://news.naver.com/"
    
    # HTTP 요청을 보내고 응답 받기
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 핫이슈 기사를 포함하는 영역을 찾아내기
    hot_issue_section = soup.find('ul', {'class': 'hot_issue_list'})
    
    # 핫이슈 기사 링크 및 제목 추출
    hot_issues = hot_issue_section.find_all('li', limit=30)  # 30개까지 기사 추출
    
    for issue in hot_issues:
        title = issue.find('a').text.strip()
        link = issue.find('a')['href']
        
        # 뉴스 본문 스크래핑 (상세 페이지로 이동하여 본문 가져오기)
        news_response = requests.get(link)
        news_soup = BeautifulSoup(news_response.text, 'html.parser')
        content = news_soup.find('div', {'class': 'news_body'}).text.strip()  # 뉴스 본문 추출
        
        # News 모델에 저장
        news = News(
            title=title,
            content=content,
            source_url=link,
            created_at=datetime.utcnow()
        )

        db.session.add(news)

    db.session.commit()
    print("핫이슈 30개 스크래핑 완료!")