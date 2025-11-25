from langchain_core.documents import Document
from app.rag.vectorstore import get_vectorstore_manager
from app.models.schemas import TopicCategory, DifficultyLevel


class PythonEducationRetriever:
    """Python 교육용 RAG Retriever"""

    def __init__(self):
        self.vectorstore_manager = get_vectorstore_manager()

    def retrieve(
        self,
        query: str,
        topic: TopicCategory = None,
        difficulty: DifficultyLevel = None,
        k: int = 4,
    ) -> list[Document]:
        """
        쿼리에 맞는 문서 검색

        Args:
            query: 검색 쿼리
            topic: 주제 필터 (선택)
            difficulty: 난이도 필터 (선택)
            k: 반환할 문서 수

        Returns:
            관련 문서 리스트
        """
        # 쿼리 향상 - 주제와 난이도 정보 추가
        enhanced_query = query
        if topic:
            topic_korean = {
                TopicCategory.BASICS: "파이썬 기초 문법",
                TopicCategory.DATA_STRUCTURES: "자료구조",
                TopicCategory.ALGORITHMS: "알고리즘",
                TopicCategory.OOP: "객체지향 프로그래밍",
                TopicCategory.FILE_IO: "파일 입출력",
                TopicCategory.EXCEPTIONS: "예외 처리",
                TopicCategory.MODULES: "모듈과 패키지",
                TopicCategory.FUNCTIONS: "함수",
            }
            enhanced_query = f"{topic_korean.get(topic, topic.value)} {enhanced_query}"

        if difficulty:
            difficulty_korean = {
                DifficultyLevel.BEGINNER: "입문 초급",
                DifficultyLevel.INTERMEDIATE: "중급",
                DifficultyLevel.ADVANCED: "고급 심화",
            }
            enhanced_query = (
                f"{difficulty_korean.get(difficulty, difficulty.value)} {enhanced_query}"
            )

        # 유사도 검색
        documents = self.vectorstore_manager.similarity_search(enhanced_query, k=k)

        return documents

    def retrieve_for_problem(
        self,
        topic: TopicCategory,
        difficulty: DifficultyLevel,
        problem_type: str,
    ) -> list[Document]:
        """문제 출제를 위한 문서 검색"""
        query = f"{topic.value} {difficulty.value} {problem_type} 문제 예제"
        return self.retrieve(query, topic, difficulty, k=6)

    def retrieve_for_explanation(
        self,
        topic: TopicCategory,
        concept: str,
    ) -> list[Document]:
        """개념 설명을 위한 문서 검색"""
        query = f"{concept} 개념 설명 예제"
        return self.retrieve(query, topic, k=4)

    def get_context_string(self, documents: list[Document]) -> str:
        """문서 리스트를 컨텍스트 문자열로 변환"""
        if not documents:
            return "관련 문서를 찾을 수 없습니다."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "알 수 없음")
            context_parts.append(f"[문서 {i}] (출처: {source})\n{doc.page_content}")

        return "\n\n---\n\n".join(context_parts)


# 싱글톤 인스턴스
_retriever = None


def get_retriever() -> PythonEducationRetriever:
    global _retriever
    if _retriever is None:
        _retriever = PythonEducationRetriever()
    return _retriever
