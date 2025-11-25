import json
import uuid
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_anthropic import ChatAnthropic

from app.config import get_settings
from app.rag.retriever import get_retriever
from app.models.schemas import (
    TopicCategory,
    DifficultyLevel,
    ProblemType,
    Problem,
)


PROBLEM_GENERATION_PROMPT = """당신은 컴퓨터공학과 학생들을 위한 Python 문제 출제 전문가입니다.

## 출제 조건
- 주제: {topic}
- 난이도: {difficulty}
- 문제 유형: {problem_type}
- 출제 개수: {count}개

## 문제 유형별 형식

### 객관식 (multiple_choice)
- 4개의 선택지 제공
- 정답은 1개

### 코딩 (coding)
- 함수 구현 문제
- 입력/출력 예시 포함
- 테스트 케이스 제시

### 디버깅 (debugging)
- 버그가 있는 코드 제시
- 버그를 찾아 수정하는 문제

### 알고리즘 (algorithm)
- 알고리즘 구현 문제
- 시간/공간 복잡도 고려
- 효율적인 해결책 요구

### 단답형 (short_answer)
- 개념이나 결과를 묻는 문제
- 짧은 답변 요구

## 참고 자료
{context}

## 응답 형식
반드시 다음 JSON 형식으로만 응답하세요. 다른 텍스트는 포함하지 마세요:

```json
{{
  "problems": [
    {{
      "question": "문제 내용",
      "options": ["선택지1", "선택지2", "선택지3", "선택지4"],  // 객관식인 경우만
      "answer": "정답",
      "explanation": "해설",
      "hints": ["힌트1", "힌트2"]
    }}
  ]
}}
```

객관식이 아닌 경우 "options" 필드는 생략하세요.
코딩/알고리즘 문제의 answer에는 정답 코드를 포함하세요.
"""


def get_llm():
    """설정에 따라 LLM 인스턴스 반환"""
    settings = get_settings()

    if settings.llm_provider == "ollama":
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.8,
        )
    else:
        return ChatAnthropic(
            model=settings.anthropic_model,
            anthropic_api_key=settings.anthropic_api_key,
            temperature=0.8,
            max_tokens=4096,
        )


class ProblemAgent:
    """문제 출제 에이전트"""

    def __init__(self):
        self.settings = get_settings()
        self.llm = get_llm()
        self.retriever = get_retriever()

    def _get_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", PROBLEM_GENERATION_PROMPT),
            ("human", "위 조건에 맞는 문제를 생성해주세요."),
        ])

    def _parse_response(
        self,
        response: str,
        topic: TopicCategory,
        difficulty: DifficultyLevel,
        problem_type: ProblemType,
    ) -> list[Problem]:
        """LLM 응답을 Problem 객체로 파싱"""
        try:
            # JSON 부분 추출
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("JSON not found in response")

            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            problems = []
            for p in data.get("problems", []):
                problem = Problem(
                    id=str(uuid.uuid4()),
                    topic=topic,
                    difficulty=difficulty,
                    problem_type=problem_type,
                    question=p.get("question", ""),
                    options=p.get("options"),
                    answer=p.get("answer", ""),
                    explanation=p.get("explanation", ""),
                    hints=p.get("hints", []),
                )
                problems.append(problem)

            return problems

        except (json.JSONDecodeError, KeyError) as e:
            # 파싱 실패 시 빈 리스트 반환
            print(f"Failed to parse response: {e}")
            return []

    async def generate_problems(
        self,
        topic: TopicCategory,
        difficulty: DifficultyLevel,
        problem_type: ProblemType,
        count: int = 1,
    ) -> list[Problem]:
        """
        문제 생성

        Args:
            topic: 주제
            difficulty: 난이도
            problem_type: 문제 유형
            count: 생성할 문제 수

        Returns:
            생성된 문제 리스트
        """
        # RAG로 관련 문서 검색
        documents = self.retriever.retrieve_for_problem(
            topic, difficulty, problem_type.value
        )
        context = self.retriever.get_context_string(documents)

        # 프롬프트 생성
        prompt = self._get_prompt()

        # 체인 실행
        chain = prompt | self.llm | StrOutputParser()

        response = await chain.ainvoke({
            "topic": self._get_topic_korean(topic),
            "difficulty": self._get_difficulty_korean(difficulty),
            "problem_type": self._get_problem_type_korean(problem_type),
            "count": count,
            "context": context,
        })

        return self._parse_response(response, topic, difficulty, problem_type)

    def generate_problems_sync(
        self,
        topic: TopicCategory,
        difficulty: DifficultyLevel,
        problem_type: ProblemType,
        count: int = 1,
    ) -> list[Problem]:
        """동기 버전의 문제 생성"""
        # RAG로 관련 문서 검색
        documents = self.retriever.retrieve_for_problem(
            topic, difficulty, problem_type.value
        )
        context = self.retriever.get_context_string(documents)

        # 프롬프트 생성
        prompt = self._get_prompt()

        # 체인 실행
        chain = prompt | self.llm | StrOutputParser()

        response = chain.invoke({
            "topic": self._get_topic_korean(topic),
            "difficulty": self._get_difficulty_korean(difficulty),
            "problem_type": self._get_problem_type_korean(problem_type),
            "count": count,
            "context": context,
        })

        return self._parse_response(response, topic, difficulty, problem_type)

    def _get_topic_korean(self, topic: TopicCategory) -> str:
        mapping = {
            TopicCategory.BASICS: "파이썬 기초 문법 (변수, 자료형, 연산자, 조건문, 반복문)",
            TopicCategory.DATA_STRUCTURES: "자료구조 (리스트, 딕셔너리, 집합, 튜플, 스택, 큐)",
            TopicCategory.ALGORITHMS: "알고리즘 (정렬, 탐색, 재귀, 동적 프로그래밍)",
            TopicCategory.OOP: "객체지향 프로그래밍 (클래스, 상속, 다형성, 캡슐화)",
            TopicCategory.FILE_IO: "파일 입출력 (파일 읽기/쓰기, CSV, JSON)",
            TopicCategory.EXCEPTIONS: "예외 처리 (try-except, raise, 사용자 정의 예외)",
            TopicCategory.MODULES: "모듈과 패키지 (import, pip, 가상환경)",
            TopicCategory.FUNCTIONS: "함수 (매개변수, 반환값, 람다, 데코레이터)",
        }
        return mapping.get(topic, topic.value)

    def _get_difficulty_korean(self, difficulty: DifficultyLevel) -> str:
        mapping = {
            DifficultyLevel.BEGINNER: "입문 (쉬운 난이도, 기본 개념)",
            DifficultyLevel.INTERMEDIATE: "중급 (보통 난이도, 응용)",
            DifficultyLevel.ADVANCED: "고급 (어려운 난이도, 심화)",
        }
        return mapping.get(difficulty, difficulty.value)

    def _get_problem_type_korean(self, problem_type: ProblemType) -> str:
        mapping = {
            ProblemType.MULTIPLE_CHOICE: "객관식",
            ProblemType.CODING: "코딩 (함수 구현)",
            ProblemType.DEBUGGING: "디버깅 (버그 수정)",
            ProblemType.ALGORITHM: "알고리즘 구현",
            ProblemType.SHORT_ANSWER: "단답형",
        }
        return mapping.get(problem_type, problem_type.value)


# 싱글톤 인스턴스
_problem_agent = None


def get_problem_agent() -> ProblemAgent:
    global _problem_agent
    if _problem_agent is None:
        _problem_agent = ProblemAgent()
    return _problem_agent
