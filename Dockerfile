# 프로덕션 Docker 이미지 for Python 교육 에이전트

# Python 3.12 slim 이미지 사용
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 8501 노출 (Streamlit 기본 포트)
EXPOSE 8501

# 건강 상태 체크
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 실행 명령어
ENTRYPOINT ["streamlit", "run", "frontend/streamlit_app.py", "--server.headless", "true", "--server.address", "0.0.0.0", "--server.port", "8501"]