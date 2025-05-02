## pagination.py
# 페이지네이션 유틸리티

def paginate(queryset, page, per_page=10):
    """쿼리셋을 페이지 단위로 나누기"""
    total_items = len(queryset)
    start = (page - 1) * per_page
    end = start + per_page
    return queryset[start:end], total_items