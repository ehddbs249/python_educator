# 🚀 Python 교육 에이전트 배포 가이드

## 필수 환경 변수

배포 시 다음 환경 변수들을 반드시 설정해야 합니다:

```bash
# LLM Provider 설정 (필수)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LLM_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-3-5-haiku-20241022

# 데이터베이스 설정 (필수)
DATABASE_PROVIDER=supabase
SUPABASE_URL=https://beipxotlrsvibdwddqka.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# 기타 설정 (선택)
DEBUG=false
PORT=8501
```

## 🎯 추천 배포 방법: Streamlit Community Cloud

### 장점
- ✅ 완전 무료
- ✅ GitHub 자동 연동
- ✅ SSL/HTTPS 자동 설정
- ✅ 커스텀 도메인 지원

### 배포 단계

1. **코드 GitHub에 업로드**
```bash
git add .
git commit -m "feat: 프로덕션 배포 준비"
git push origin main
```

2. **Streamlit Community Cloud 접속**
   - https://share.streamlit.io 방문
   - GitHub 계정으로 로그인

3. **앱 생성**
   - "New app" 버튼 클릭
   - Repository: `python_educator`
   - Branch: `main`
   - Main file path: `frontend/streamlit_app.py`

4. **환경 변수 설정**
   - "Advanced settings" 클릭
   - "Secrets" 탭에서 다음 내용 추가:

```toml
ANTHROPIC_API_KEY = "your_anthropic_key"
SUPABASE_URL = "https://beipxotlrsvibdwddqka.supabase.co"
SUPABASE_KEY = "your_supabase_key"
DATABASE_PROVIDER = "supabase"
LLM_PROVIDER = "anthropic"
ANTHROPIC_MODEL = "claude-3-5-haiku-20241022"
```

5. **배포 완료!**
   - 몇 분 후 자동으로 URL이 생성됩니다
   - 예: `https://your-app-name.streamlit.app`

## 🚂 대안: Railway 배포

Railway는 더 고급 기능을 제공하지만 유료입니다.

### Railway 배포 단계

1. **Railway 가입**
   - https://railway.app 접속
   - GitHub 계정으로 가입

2. **프로젝트 연결**
   - "New Project" → "Deploy from GitHub repo"
   - `python_educator` repository 선택

3. **환경 변수 설정**
   - Settings → Environment 에서 위 환경 변수들 추가

4. **자동 배포**
   - `railway.toml` 파일이 자동으로 감지됨
   - Docker 컨테이너로 자동 빌드 및 배포

## 🔧 배포 후 확인사항

### 1. 헬스체크 확인
- `your-app-url/_stcore/health` 접속
- 정상: `{"status": "ok"}`

### 2. 데이터베이스 연결 확인
- 앱에서 로그인 시도
- 문제 생성 테스트
- 학습 기록 저장 확인

### 3. API 키 동작 확인
- 문제 생성이 정상 작동하는지 확인
- 코드 리뷰 기능 테스트

## 🛠️ 문제 해결

### 자주 발생하는 오류

1. **Module not found 오류**
   - `requirements.txt` 확인
   - 모든 의존성이 포함되었는지 확인

2. **환경 변수 오류**
   - 대소문자 정확히 확인
   - 따옴표 사용 여부 확인

3. **Supabase 연결 오류**
   - URL이 정확한지 확인
   - API 키가 유효한지 확인
   - RLS 정책이 활성화되었는지 확인

## 📱 모바일 최적화

앱은 모바일 환경에서도 잘 작동하도록 최적화되어 있습니다:
- 반응형 디자인
- 터치 스크린 최적화
- 모바일 키보드 지원

## 🔒 보안 고려사항

1. **환경 변수 보안**
   - API 키를 코드에 직접 포함하지 마세요
   - GitHub Secrets 또는 배포 플랫폼의 환경 변수 기능 사용

2. **Supabase RLS**
   - Row Level Security가 활성화되어 있어 사용자 데이터가 보호됩니다

3. **HTTPS**
   - 모든 배포 플랫폼이 자동으로 SSL/HTTPS를 제공합니다

## 🎉 완료!

배포가 성공하면 다른 사람들이 인터넷을 통해 여러분의 Python 교육 에이전트에 접속할 수 있습니다!

URL을 공유하여 학생들이나 동료들과 함께 사용해보세요.