import sys
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import get_settings
from app.models.schemas import CodeReviewResult, Problem


CODE_REVIEW_PROMPT = """당신은 Python 코드 리뷰 전문가입니다.

## 역할
학생이 제출한 코드를 분석하고 피드백을 제공합니다.

## 문제 정보
{problem_info}

## 학생이 제출한 코드
```python
{submitted_code}
```

## 코드 실행 결과
{execution_result}

## 리뷰 기준
1. **정확성**: 코드가 문제의 요구사항을 충족하는가?
2. **효율성**: 시간/공간 복잡도가 적절한가?
3. **가독성**: 코드가 읽기 쉽고 이해하기 쉬운가?
4. **파이썬다움**: Python의 관용적 표현(Pythonic)을 사용했는가?
5. **에러 처리**: 예외 상황을 적절히 처리했는가?

## 응답 형식
다음 형식으로 응답하세요:

### 정답 여부
[정답/오답/부분 정답]

### 점수
[0-100점]

### 피드백
[상세한 피드백]

### 개선 제안
- [제안 1]
- [제안 2]

### 개선된 코드 (필요한 경우)
```python
[개선된 코드]
```
"""

GENERAL_REVIEW_PROMPT = """당신은 Python 코드 리뷰 전문가입니다.

## 역할
학생이 제출한 코드를 분석하고 피드백을 제공합니다.

## 학생이 제출한 코드
```python
{submitted_code}
```

## 코드 실행 결과
{execution_result}

## 리뷰 기준
1. **정확성**: 코드가 의도한 대로 동작하는가?
2. **효율성**: 더 효율적인 방법이 있는가?
3. **가독성**: 코드가 읽기 쉽고 이해하기 쉬운가?
4. **파이썬다움**: Python의 관용적 표현(Pythonic)을 사용했는가?
5. **에러 처리**: 예외 상황을 적절히 처리했는가?
6. **보안**: 보안 취약점이 있는가?

## 응답 형식
다음 형식으로 응답하세요:

### 점수
[0-100점]

### 전반적인 평가
[코드에 대한 전반적인 평가]

### 잘한 점
- [잘한 점 1]
- [잘한 점 2]

### 개선이 필요한 점
- [개선점 1]
- [개선점 2]

### 개선된 코드 (필요한 경우)
```python
[개선된 코드]
```

### 추가 학습 제안
[관련 개념이나 학습 자료 제안]
"""


class CodeReviewAgent:
    """코드 리뷰 에이전트"""

    def __init__(self):
        self.settings = get_settings()
        self.llm = ChatAnthropic(
            model=self.settings.model_name,
            anthropic_api_key=self.settings.anthropic_api_key,
            temperature=0.3,  # 일관된 리뷰를 위해 낮게
            max_tokens=4096,
        )

    def _safe_execute_code(self, code: str, timeout: int = 5) -> dict:
        """
        코드를 안전하게 실행하고 결과 반환

        Args:
            code: 실행할 코드
            timeout: 제한 시간 (초)

        Returns:
            실행 결과 딕셔너리
        """
        result = {
            "success": False,
            "output": "",
            "error": "",
        }

        # stdout, stderr 캡처
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        try:
            # 제한된 전역 네임스페이스
            restricted_globals = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "range": range,
                    "enumerate": enumerate,
                    "zip": zip,
                    "map": map,
                    "filter": filter,
                    "sorted": sorted,
                    "reversed": reversed,
                    "sum": sum,
                    "min": min,
                    "max": max,
                    "abs": abs,
                    "round": round,
                    "int": int,
                    "float": float,
                    "str": str,
                    "bool": bool,
                    "list": list,
                    "dict": dict,
                    "set": set,
                    "tuple": tuple,
                    "type": type,
                    "isinstance": isinstance,
                    "input": lambda x="": "",  # input은 빈 문자열 반환
                    "True": True,
                    "False": False,
                    "None": None,
                },
            }

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, restricted_globals)

            result["success"] = True
            result["output"] = stdout_capture.getvalue()

        except Exception as e:
            result["error"] = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"

        return result

    def _parse_review_response(self, response: str) -> CodeReviewResult:
        """리뷰 응답 파싱"""
        # 기본값
        is_correct = False
        score = 50
        feedback = response
        suggestions = []
        improved_code = None

        # 점수 추출
        if "### 점수" in response:
            try:
                score_section = response.split("### 점수")[1].split("###")[0]
                score_str = "".join(filter(str.isdigit, score_section.split("\n")[1]))
                if score_str:
                    score = min(100, max(0, int(score_str)))
            except (IndexError, ValueError):
                pass

        # 정답 여부 추출
        if "### 정답 여부" in response:
            correct_section = response.split("### 정답 여부")[1].split("###")[0].lower()
            is_correct = "정답" in correct_section and "오답" not in correct_section

        # 피드백 추출
        if "### 피드백" in response:
            feedback = response.split("### 피드백")[1].split("###")[0].strip()
        elif "### 전반적인 평가" in response:
            feedback = response.split("### 전반적인 평가")[1].split("###")[0].strip()

        # 개선 제안 추출
        if "### 개선 제안" in response or "### 개선이 필요한 점" in response:
            try:
                if "### 개선 제안" in response:
                    suggestions_section = response.split("### 개선 제안")[1].split("###")[0]
                else:
                    suggestions_section = response.split("### 개선이 필요한 점")[1].split("###")[0]

                for line in suggestions_section.split("\n"):
                    line = line.strip()
                    if line.startswith("- "):
                        suggestions.append(line[2:])
            except IndexError:
                pass

        # 개선된 코드 추출
        if "### 개선된 코드" in response:
            try:
                code_section = response.split("### 개선된 코드")[1]
                if "```python" in code_section:
                    improved_code = code_section.split("```python")[1].split("```")[0].strip()
                elif "```" in code_section:
                    improved_code = code_section.split("```")[1].split("```")[0].strip()
            except IndexError:
                pass

        return CodeReviewResult(
            is_correct=is_correct,
            score=score,
            feedback=feedback,
            suggestions=suggestions,
            improved_code=improved_code,
        )

    async def review_submission(
        self,
        code: str,
        problem: Problem = None,
    ) -> CodeReviewResult:
        """
        제출된 코드 리뷰

        Args:
            code: 제출된 코드
            problem: 문제 정보 (선택)

        Returns:
            코드 리뷰 결과
        """
        # 코드 실행
        execution_result = self._safe_execute_code(code)
        execution_str = self._format_execution_result(execution_result)

        # 프롬프트 선택
        if problem:
            prompt = ChatPromptTemplate.from_messages([
                ("system", CODE_REVIEW_PROMPT),
                ("human", "위 코드를 리뷰해주세요."),
            ])
            problem_info = f"""
문제: {problem.question}
정답: {problem.answer}
난이도: {problem.difficulty.value}
주제: {problem.topic.value}
"""
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", GENERAL_REVIEW_PROMPT),
                ("human", "위 코드를 리뷰해주세요."),
            ])
            problem_info = "일반 코드 리뷰 (특정 문제 없음)"

        # 체인 실행
        chain = prompt | self.llm | StrOutputParser()

        response = await chain.ainvoke({
            "problem_info": problem_info,
            "submitted_code": code,
            "execution_result": execution_str,
        })

        return self._parse_review_response(response)

    def review_submission_sync(
        self,
        code: str,
        problem: Problem = None,
    ) -> CodeReviewResult:
        """동기 버전의 코드 리뷰"""
        # 코드 실행
        execution_result = self._safe_execute_code(code)
        execution_str = self._format_execution_result(execution_result)

        # 프롬프트 선택
        if problem:
            prompt = ChatPromptTemplate.from_messages([
                ("system", CODE_REVIEW_PROMPT),
                ("human", "위 코드를 리뷰해주세요."),
            ])
            problem_info = f"""
문제: {problem.question}
정답: {problem.answer}
난이도: {problem.difficulty.value}
주제: {problem.topic.value}
"""
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", GENERAL_REVIEW_PROMPT),
                ("human", "위 코드를 리뷰해주세요."),
            ])
            problem_info = "일반 코드 리뷰 (특정 문제 없음)"

        # 체인 실행
        chain = prompt | self.llm | StrOutputParser()

        response = chain.invoke({
            "problem_info": problem_info,
            "submitted_code": code,
            "execution_result": execution_str,
        })

        return self._parse_review_response(response)

    def _format_execution_result(self, result: dict) -> str:
        """실행 결과 포맷팅"""
        if result["success"]:
            output = result["output"] if result["output"] else "(출력 없음)"
            return f"✅ 실행 성공\n출력:\n{output}"
        else:
            return f"❌ 실행 실패\n에러:\n{result['error']}"


# 싱글톤 인스턴스
_review_agent = None


def get_review_agent() -> CodeReviewAgent:
    global _review_agent
    if _review_agent is None:
        _review_agent = CodeReviewAgent()
    return _review_agent
