import requests
from bs4 import BeautifulSoup
from datetime import datetime
from services.news_service import save_news_to_db

# 네이버 뉴스 카테고리 URL 목록
NAVER_NEWS_CATEGORIES = {
    "politics": "https://news.naver.com/section/100",
    "economy": "https://news.naver.com/section/101",
    "domestic": "https://news.naver.com/section/102",
    "world": "https://news.naver.com/section/104",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_article_content(url):
    """기사 상세 내용을 가져오는 함수"""
    try:
        # URL이 /n.news.naver.com으로 시작하면 https://를 추가
        if url.startswith("/n.news.naver.com"):
            url = f"https:{url}"
            
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code != 200:
            print(f"⚠️ 기사 접근 실패: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        
        # 기본 메타 정보
        category_tag = soup.select_one(".media_end_categorize_item")
        date_tag = soup.select_one(".media_end_head_info_datestamp_time")
        source_tag = soup.select_one(".media_end_head_top_logo_text")
        author_tag = soup.select_one(".media_end_head_journalist_name")
        author_email = soup.select_one(".byline_s")
        
        # 기사 요약
        summary = soup.select_one(".media_end_summary")
        summary_text = summary.get_text(strip=True) if summary else ""
        
        # 본문 내용
        content_area = soup.select_one("#dic_area")
        if not content_area:
            print(f"⚠️ 기사 본문을 찾을 수 없음: {url}")
            return None
            
        # 이미지 정보 수집
        images = []
        for img_div in content_area.select(".end_photo_org"):
            img = img_div.select_one("img")
            if img:
                caption = img_div.select_one(".img_desc")
                images.append({
                    "url": img.get("src", ""),
                    "alt": img.get("alt", ""),
                    "caption": caption.get_text(strip=True) if caption else None
                })
        
        # 본문 텍스트 추출
        content_text = []
        for element in content_area.contents:
            if element.name == "span" and "end_photo_org" in element.get("class", []):
                continue  # 이미지 건너뛰기
            elif element.name == "br":
                content_text.append("\n")
            elif isinstance(element, str):
                text = element.strip()
                if text:
                    content_text.append(text)
            elif element.name is None:
                text = element.strip()
                if text:
                    content_text.append(text)
                    
        content_text = " ".join(content_text).strip()
        
        # 원문 URL과 저작권
        original_url = soup.select_one(".media_end_head_origin_link")
        copyright = soup.select_one(".copyright .c_text")
        
        return {
            "category": category_tag.get_text(strip=True) if category_tag else None,
            "published_at": date_tag.get("data-date-time") if date_tag else None,
            "source": source_tag.get_text(strip=True) if source_tag else None,
            "author": author_tag.get_text(strip=True) if author_tag else None,
            "author_email": author_email.get_text(strip=True) if author_email else None,
            "summary": summary_text,
            "content": content_text,
            "images": images,
            "original_url": original_url["href"] if original_url else None,
            "copyright": copyright.get_text(strip=True) if copyright else None
        }
        
    except Exception as e:
        print(f"⚠️ 기사 내용 가져오기 실패: {e}")
        return None

def scrape_naver_news(category_url, category):
    """카테고리별 뉴스 스크래핑 함수"""
    print(f"🔍 {category} 뉴스 스크래핑 시작: {datetime.now()}")
    news_list = []

    try:
        response = requests.get(category_url, headers=HEADERS, timeout=5)
        if response.status_code != 200:
            print(f"❌ {category} 뉴스 가져오기 실패: {response.status_code}")
            return news_list

        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.select("li.sa_item")  # 뉴스 기사 목록

        for article in articles:
            try:
                title_tag = article.select_one("a.sa_text_title")
                link_tag = article.select_one("a.sa_text_title")
                press_tag = article.select_one("div.sa_text_press")
                
                if not title_tag or not link_tag:
                    continue

                link = link_tag["href"] if link_tag.has_attr("href") else ""
                
                # 기사 상세 내용 가져오기
                article_detail = get_article_content(link)
                if not article_detail:
                    continue

                news_item = {
                    "category": category,
                    "title": title_tag.get_text(strip=True),
                    "source_url": link,
                    "source": press_tag.get_text(strip=True) if press_tag else "출처 없음",
                    "published_at": datetime.now(),
                    "content": article_detail["content"],
                    "images": article_detail["images"],
                    "author": article_detail["author"],
                    "author_email": article_detail["author_email"],
                    "original_url": article_detail["original_url"],
                    "copyright": article_detail["copyright"],
                    "views": 0
                }
                news_list.append(news_item)

            except Exception as e:
                print(f"⚠️ {category} 뉴스 처리 중 오류 발생: {e}")
                continue

        # DB 저장
        save_news_to_db(news_list)
        print(f"✅ {category} 뉴스 스크래핑 완료!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ {category} 뉴스 요청 실패: {e}")

    return news_list

def main():
    """모든 카테고리 뉴스 스크래핑 실행"""
    # 각 카테고리별 뉴스 스크래핑
    for category, url in NAVER_NEWS_CATEGORIES.items():
        try:
            scrape_naver_news(url, category)
        except Exception as e:
            print(f"❌ {category} 카테고리 스크래핑 실패: {e}")

if __name__ == "__main__":
    main()