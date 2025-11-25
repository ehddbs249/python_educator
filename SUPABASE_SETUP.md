# Supabase 설정 및 배포 가이드

이 가이드는 Python 교육 에이전트를 Supabase에 배포하는 방법을 설명합니다.

## 1. Supabase 프로젝트 설정

### 1.1 Supabase 계정 생성
1. [Supabase](https://supabase.com)에 접속하여 계정 생성
2. 새 프로젝트 생성

### 1.2 데이터베이스 스키마 생성
1. Supabase 대시보드에서 SQL Editor 열기
2. `supabase_schema.sql` 파일의 내용을 복사하여 실행

```sql
-- supabase_schema.sql 파일 내용 전체 실행
```

### 1.3 API 키 확인
Supabase 대시보드의 Settings > API에서 다음을 확인:
- `Project URL`: `https://your-project-ref.supabase.co`
- `anon public key`: 공개 키
- `service_role key`: 서비스 키 (관리자용)

## 2. 환경 변수 설정

### 2.1 .env 파일 생성
```bash
cp .env.example .env
```

### 2.2 .env 파일 편집
```bash
# Supabase Settings
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_role_key_here

# Database Provider 변경
DATABASE_PROVIDER=supabase
```

## 3. 데이터 마이그레이션 (선택사항)

기존 SQLite 데이터가 있는 경우:

```bash
python migrate_to_supabase.py
```

## 4. 로컬 테스트

### 4.1 의존성 설치
```bash
pip install -r requirements.txt
```

### 4.2 앱 실행
```bash
streamlit run frontend/streamlit_app.py
```

## 5. Supabase에 배포

### 5.1 Streamlit Community Cloud 배포

1. GitHub 리포지토리에 코드 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud)에서 새 앱 배포
3. Environment variables에 다음 추가:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   DATABASE_PROVIDER=supabase
   ANTHROPIC_API_KEY=your_anthropic_key
   ```

### 5.2 다른 플랫폼 배포

#### Railway
```bash
# railway.toml 생성 후
railway deploy
```

#### Heroku
```bash
# Procfile 생성 후
heroku create your-app-name
heroku config:set SUPABASE_URL=your_url
heroku config:set SUPABASE_KEY=your_key
heroku config:set DATABASE_PROVIDER=supabase
git push heroku main
```

#### Vercel
```bash
# vercel.json 생성 후
vercel --env SUPABASE_URL=your_url --env SUPABASE_KEY=your_key
```

## 6. 프로덕션 고려사항

### 6.1 Row Level Security (RLS)
- RLS가 활성화되어 있어 보안이 강화됨
- 필요에 따라 인증 시스템 추가 고려

### 6.2 데이터베이스 백업
- Supabase 자동 백업 활용
- 중요한 데이터는 별도 백업 권장

### 6.3 API 키 관리
- 환경변수로 관리하여 코드에 노출 금지
- Service role key는 서버 사이드에서만 사용

### 6.4 성능 최적화
- 데이터베이스 인덱스 최적화
- Connection pooling 고려
- 캐싱 전략 수립

## 7. 모니터링

### 7.1 Supabase 대시보드
- 실시간 요청 모니터링
- 데이터베이스 사용량 확인
- 에러 로그 모니터링

### 7.2 애플리케이션 로깅
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## 8. 문제 해결

### 8.1 연결 에러
- API 키 확인
- 네트워크 연결 확인
- RLS 정책 확인

### 8.2 권한 에러
- RLS 정책 검토
- API 키 권한 확인

### 8.3 성능 문제
- 쿼리 최적화
- 인덱스 추가
- 페이지네이션 구현

## 참고 링크

- [Supabase 공식 문서](https://supabase.com/docs)
- [Streamlit 배포 가이드](https://docs.streamlit.io/streamlit-community-cloud)
- [Python Supabase 클라이언트](https://github.com/supabase/supabase-py)