# /home/livon/projects/today_talk/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 필요한 디렉터리 생성
RUN mkdir -p static/uploads

EXPOSE 5003

CMD ["python", "app.py"]