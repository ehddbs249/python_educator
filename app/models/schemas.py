from pydantic import BaseModel
from enum import Enum
from typing import Optional


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"  # 입문
    INTERMEDIATE = "intermediate"  # 중급
    ADVANCED = "advanced"  # 고급


class ProblemType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"  # 객관식
    CODING = "coding"  # 코딩 문제
    DEBUGGING = "debugging"  # 디버깅
    ALGORITHM = "algorithm"  # 알고리즘
    SHORT_ANSWER = "short_answer"  # 단답형


class TopicCategory(str, Enum):
    BASICS = "basics"  # 기초 문법
    DATA_STRUCTURES = "data_structures"  # 자료구조
    ALGORITHMS = "algorithms"  # 알고리즘
    OOP = "oop"  # 객체지향
    FILE_IO = "file_io"  # 파일 입출력
    EXCEPTIONS = "exceptions"  # 예외 처리
    MODULES = "modules"  # 모듈과 패키지
    FUNCTIONS = "functions"  # 함수


class ChatMessage(BaseModel):
    """채팅 메시지"""
    role: str  # user, assistant
    content: str


class ProblemRequest(BaseModel):
    """문제 출제 요청"""
    topic: TopicCategory
    difficulty: DifficultyLevel
    problem_type: ProblemType
    count: int = 1


class Problem(BaseModel):
    """문제"""
    id: str
    topic: TopicCategory
    difficulty: DifficultyLevel
    problem_type: ProblemType
    question: str
    options: Optional[list[str]] = None  # 객관식인 경우
    answer: str
    explanation: str
    hints: list[str] = []


class CodeSubmission(BaseModel):
    """코드 제출"""
    problem_id: Optional[str] = None
    code: str
    language: str = "python"


class CodeReviewResult(BaseModel):
    """코드 리뷰 결과"""
    is_correct: bool
    score: int  # 0-100
    feedback: str
    suggestions: list[str] = []
    improved_code: Optional[str] = None


class LearningRequest(BaseModel):
    """학습 요청"""
    topic: TopicCategory
    difficulty: DifficultyLevel
    question: Optional[str] = None
