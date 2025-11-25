from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_models import ChatOllama
from langchain_anthropic import ChatAnthropic

from app.config import get_settings
from app.rag.retriever import get_retriever
from app.models.schemas import TopicCategory, DifficultyLevel


TEACHER_SYSTEM_PROMPT = """당신은 컴퓨터공학과 학생들을 위한 Python 교육 전문가입니다.

## 역할
- 학생들의 수준에 맞춰 Python 개념을 친절하고 명확하게 설명합니다.
- 실용적인 예제 코드를 제공합니다.
- 학생들이 이해하기 쉽도록 단계별로 설명합니다.

## 교육 스타일
- 난이도: {difficulty}
- 주제: {topic}

## 난이도별 설명 방식
- beginner (입문): 기초 개념부터 차근차근, 많은 예제와 비유 사용
- intermediate (중급): 핵심 개념 위주, 실무 활용 예제 포함
- advanced (고급): 심화 내용, 최적화, 베스트 프랙티스 중심

## 참고 자료
다음은 관련 교육 자료입니다:
{context}

## 응답 형식
1. 개념 설명
2. 예제 코드 (```python 코드블록 사용)
3. 핵심 포인트 요약
4. 추가 학습 제안 (선택적)

항상 한국어로 응답하세요.
"""


def get_llm():
    """설정에 따라 LLM 인스턴스 반환"""
    settings = get_settings()

    if settings.llm_provider == "ollama":
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.7,
        )
    else:
        return ChatAnthropic(
            model=settings.anthropic_model,
            anthropic_api_key=settings.anthropic_api_key,
            temperature=0.7,
            max_tokens=4096,
        )


class TeacherAgent:
    """Python 교육 에이전트"""

    def __init__(self):
        self.settings = get_settings()
        self.llm = get_llm()
        self.retriever = get_retriever()

    def _get_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", TEACHER_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ])

    def _format_chat_history(self, chat_history: list[dict]) -> list:
        """채팅 히스토리를 LangChain 메시지 형식으로 변환"""
        messages = []
        for msg in chat_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        return messages

    async def teach(
        self,
        question: str,
        topic: TopicCategory = TopicCategory.BASICS,
        difficulty: DifficultyLevel = DifficultyLevel.BEGINNER,
        chat_history: list[dict] = None,
    ) -> str:
        """
        학생의 질문에 답변

        Args:
            question: 학생의 질문
            topic: 주제
            difficulty: 난이도
            chat_history: 이전 대화 기록

        Returns:
            교육 응답
        """
        if chat_history is None:
            chat_history = []

        # RAG로 관련 문서 검색
        documents = self.retriever.retrieve_for_explanation(topic, question)
        context = self.retriever.get_context_string(documents)

        # 프롬프트 생성
        prompt = self._get_prompt()

        # 체인 실행
        chain = prompt | self.llm

        response = await chain.ainvoke({
            "topic": self._get_topic_korean(topic),
            "difficulty": self._get_difficulty_korean(difficulty),
            "context": context,
            "chat_history": self._format_chat_history(chat_history),
            "question": question,
        })

        return response.content

    def teach_sync(
        self,
        question: str,
        topic: TopicCategory = TopicCategory.BASICS,
        difficulty: DifficultyLevel = DifficultyLevel.BEGINNER,
        chat_history: list[dict] = None,
    ) -> str:
        """동기 버전의 teach 메서드"""
        if chat_history is None:
            chat_history = []

        # RAG로 관련 문서 검색
        documents = self.retriever.retrieve_for_explanation(topic, question)
        context = self.retriever.get_context_string(documents)

        # 프롬프트 생성
        prompt = self._get_prompt()

        # 체인 실행
        chain = prompt | self.llm

        response = chain.invoke({
            "topic": self._get_topic_korean(topic),
            "difficulty": self._get_difficulty_korean(difficulty),
            "context": context,
            "chat_history": self._format_chat_history(chat_history),
            "question": question,
        })

        return response.content

    def _get_topic_korean(self, topic: TopicCategory) -> str:
        """주제를 한국어로 변환"""
        mapping = {
            TopicCategory.BASICS: "파이썬 기초 문법",
            TopicCategory.DATA_STRUCTURES: "자료구조",
            TopicCategory.ALGORITHMS: "알고리즘",
            TopicCategory.OOP: "객체지향 프로그래밍",
            TopicCategory.FILE_IO: "파일 입출력",
            TopicCategory.EXCEPTIONS: "예외 처리",
            TopicCategory.MODULES: "모듈과 패키지",
            TopicCategory.FUNCTIONS: "함수",
        }
        return mapping.get(topic, topic.value)

    def _get_difficulty_korean(self, difficulty: DifficultyLevel) -> str:
        """난이도를 한국어로 변환"""
        mapping = {
            DifficultyLevel.BEGINNER: "입문 (기초부터 차근차근)",
            DifficultyLevel.INTERMEDIATE: "중급 (핵심 개념 중심)",
            DifficultyLevel.ADVANCED: "고급 (심화 및 최적화)",
        }
        return mapping.get(difficulty, difficulty.value)


# 싱글톤 인스턴스
_teacher_agent = None


def get_teacher_agent() -> TeacherAgent:
    global _teacher_agent
    if _teacher_agent is None:
        _teacher_agent = TeacherAgent()
    return _teacher_agent
