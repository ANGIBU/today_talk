import unittest
from services.news_service import scrape_news


class TestNewsService(unittest.TestCase):
    def test_scrape_news(self):
        """뉴스 스크래핑 테스트"""
        news_items = scrape_news()
        self.assertIsInstance(news_items, list)  # 스크래핑 결과는 리스트여야 함
        for item in news_items:
            self.assertIn("title", item)  # 각 뉴스 항목에 제목 포함
            self.assertIn("content", item)  # 각 뉴스 항목에 내용 포함
            self.assertIn("source", item)  # 각 뉴스 항목에 출처 포함


if __name__ == "__main__":
    unittest.main()
