"""FastAPI 서버 for Python 교육 에이전트 API"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import get_db_manager
from app.agents import get_teacher_agent, get_problem_agent, get_review_agent
from app.models.schemas import (
    TopicCategory,
    DifficultyLevel,
    ProblemType,
)
from app.config import get_settings

# FastAPI 앱 초기화
app = FastAPI(
    title="Python 교육 에이전트 API",
    description="LangChain + RAG 기반 Python 학습 도우미 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 보안 설정
security = HTTPBearer()
settings = get_settings()

# Pydantic 모델들
class UserCreate(BaseModel):
    username: str

class UserResponse(BaseModel):
    id: str
    username: str
    created_at: str

class QuestionRequest(BaseModel):
    question: str
    topic: TopicCategory
    difficulty: DifficultyLevel
    user_id: str

class TeachResponse(BaseModel):
    response: str
    topic: str
    difficulty: str

class ProblemGenerateRequest(BaseModel):
    topic: TopicCategory
    difficulty: DifficultyLevel
    problem_type: ProblemType
    count: int = 1

class ProblemResponse(BaseModel):
    id: str
    topic: str
    difficulty: str
    problem_type: str
    question: str
    options: Optional[List[str]]
    answer: str
    explanation: str
    hints: Optional[List[str]]

class ProblemAttemptRequest(BaseModel):
    user_id: str
    problem_id: str
    user_answer: str

class CodeReviewRequest(BaseModel):
    code: str
    problem_id: Optional[str] = None

class CodeReviewResponse(BaseModel):
    is_correct: bool
    score: int
    feedback: str
    suggestions: List[str]
    improved_code: Optional[str]

class UserStats(BaseModel):
    total_attempts: int
    accuracy: float
    average_score: float
    by_topic: List[Dict[str, Any]]
    by_difficulty: List[Dict[str, Any]]

# 인증 헬퍼
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """현재 사용자 인증 (향후 JWT 토큰 검증으로 확장 가능)"""
    # 임시로 토큰을 user_id로 사용
    return credentials.credentials

# API 엔드포인트들

@app.get("/", tags=["Root"])
async def root():
    """API 루트 엔드포인트"""
    return {"message": "Python 교육 에이전트 API", "version": "1.0.0"}

@app.get("/health", tags=["Health"])
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "service": "python-educator-api"}

# 사용자 관리
@app.post("/users", response_model=UserResponse, tags=["Users"])
async def create_user(user: UserCreate):
    """사용자 생성"""
    try:
        db = get_db_manager()
        user_id = db.get_or_create_user(user.username)

        # 사용자 정보 조회
        user_info = db.get_user(user.username)

        return UserResponse(
            id=str(user_id),
            username=user_info.username,
            created_at=str(user_info.created_at)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}/stats", response_model=UserStats, tags=["Users"])
async def get_user_stats(user_id: str):
    """사용자 통계 조회"""
    try:
        db = get_db_manager()
        stats = db.get_user_statistics(user_id)
        return UserStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# 학습 기능
@app.post("/teach", response_model=TeachResponse, tags=["Teaching"])
async def teach(request: QuestionRequest):
    """질문에 대한 교육 응답"""
    try:
        teacher = get_teacher_agent()
        response = teacher.teach_sync(
            question=request.question,
            topic=request.topic,
            difficulty=request.difficulty,
            chat_history=[]  # API에서는 간단히 빈 히스토리로 시작
        )

        # 채팅 기록 저장
        db = get_db_manager()
        db.save_chat_message(
            user_id=request.user_id,
            role="user",
            content=request.question,
            topic=request.topic.value
        )
        db.save_chat_message(
            user_id=request.user_id,
            role="assistant",
            content=response,
            topic=request.topic.value
        )

        return TeachResponse(
            response=response,
            topic=request.topic.value,
            difficulty=request.difficulty.value
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 문제 생성 및 풀이
@app.post("/problems/generate", response_model=List[ProblemResponse], tags=["Problems"])
async def generate_problems(request: ProblemGenerateRequest):
    """문제 생성"""
    try:
        problem_agent = get_problem_agent()
        problems = problem_agent.generate_problems_sync(
            topic=request.topic,
            difficulty=request.difficulty,
            problem_type=request.problem_type,
            count=request.count
        )

        return [
            ProblemResponse(
                id=str(hash(p.question)),  # 임시 ID 생성
                topic=p.topic.value,
                difficulty=p.difficulty.value,
                problem_type=p.problem_type.value,
                question=p.question,
                options=p.options,
                answer=p.answer,
                explanation=p.explanation,
                hints=p.hints
            )
            for p in problems
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/problems/submit", tags=["Problems"])
async def submit_problem_attempt(request: ProblemAttemptRequest):
    """문제 풀이 제출 (객관식/단답형)"""
    try:
        # 여기서는 간단한 정답 체크만 구현
        # 실제로는 문제 ID로 정답을 조회해야 함

        db = get_db_manager()
        # 임시로 정답 체크 (실제 구현 시 문제 데이터에서 조회)
        is_correct = True  # 실제 로직으로 대체 필요
        score = 100 if is_correct else 0

        attempt_id = db.save_problem_attempt(
            user_id=request.user_id,
            problem_type="multiple_choice",  # 실제 문제 타입으로 대체
            topic="basics",  # 실제 주제로 대체
            difficulty="beginner",  # 실제 난이도로 대체
            question="Sample Question",  # 실제 문제로 대체
            user_answer=request.user_answer,
            correct_answer="Sample Answer",  # 실제 정답으로 대체
            is_correct=is_correct,
            score=score,
            feedback="Good job!" if is_correct else "Try again!"
        )

        return {
            "attempt_id": attempt_id,
            "is_correct": is_correct,
            "score": score,
            "feedback": "Good job!" if is_correct else "Try again!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 코드 리뷰
@app.post("/code/review", response_model=CodeReviewResponse, tags=["Code Review"])
async def review_code(request: CodeReviewRequest):
    """코드 리뷰"""
    try:
        review_agent = get_review_agent()
        result = review_agent.review_submission_sync(code=request.code)

        return CodeReviewResponse(
            is_correct=result.is_correct,
            score=result.score,
            feedback=result.feedback,
            suggestions=result.suggestions or [],
            improved_code=result.improved_code
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 에러 핸들러
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )