from models.news import News
from db import db

def save_news_to_db(news_list):
    """스크래핑된 뉴스를 DB에 저장"""
    if not news_list:
        print("ℹ️ 저장할 뉴스가 없습니다.")
        return

    with db.session.begin():
        for news_data in news_list:
            # 중복 방지: 같은 URL이 DB에 존재하는지 확인
            exists = News.query.filter_by(source_url=news_data["source_url"]).first()
            if exists:
                continue  # 중복 뉴스는 추가하지 않음

            # 새 뉴스 저장
            news = News(
                title=news_data["title"],
                content="기사 내용 없음",
                source=news_data.get("press", "출처 없음"),  # 언론사 정보가 없으면 '출처 없음'
                source_url=news_data["source_url"],
                thumbnail=news_data.get("thumbnail", None),  # 썸네일 없으면 None 저장
                published_at=news_data["published_at"],      # 발행일 저장
                category=news_data["category"],                # 스크래핑 시 문자열 카테고리 ("world", "politics" 등) 저장
                user_id=1  # 관리자 ID(예: 1)로 저장
            )
            db.session.add(news)

    print("✅ DB 저장 완료!")
