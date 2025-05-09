FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 필요한 디렉터리 생성
RUN mkdir -p static/uploads

EXPOSE 5003

CMD ["python", "app.py"]