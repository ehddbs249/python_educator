import streamlit as st
import sys
from pathlib import Path
from streamlit_ace import st_ace

# 프로젝트 루트를 path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.agents import get_teacher_agent, get_problem_agent, get_review_agent
from app.database import get_db_manager
from app.models.schemas import (
    TopicCategory,
    DifficultyLevel,
    ProblemType,
)

# 페이지 설정
st.set_page_config(
    page_title="Python 교육 에이전트",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .mode-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .problem-box {
        background-color: #e3f2fd;
        border-left: 4px solid #1E88E5;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 10px 10px 0;
    }
    .hint-box {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 10px 10px 0;
    }
    .success-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 10px 10px 0;
    }
    .error-box {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 10px 10px 0;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .weak-topic {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 0.5rem 1rem;
        margin: 0.3rem 0;
        border-radius: 0 5px 5px 0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """세션 상태 초기화"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_problem" not in st.session_state:
        st.session_state.current_problem = None
    if "hint_index" not in st.session_state:
        st.session_state.hint_index = 0
    if "mode" not in st.session_state:
        st.session_state.mode = "학습"
    if "username" not in st.session_state:
        st.session_state.username = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    # 코드 에디터 상태 초기화
    if "code_answer" not in st.session_state:
        st.session_state.code_answer = ""
    if "review_code" not in st.session_state:
        st.session_state.review_code = ""
    if "problem_code_key" not in st.session_state:
        st.session_state.problem_code_key = 0
    # 문제 풀이 결과 상태
    if "problem_result" not in st.session_state:
        st.session_state.problem_result = None  # {"is_correct": bool, "score": int, "feedback": str, "shown_answer": bool}
    if "problem_submitted" not in st.session_state:
        st.session_state.problem_submitted = False


def clear_problem_state():
    """새 문제 생성 시 이전 상태 초기화"""
    st.session_state.problem_result = None
    st.session_state.problem_submitted = False
    st.session_state.code_answer = ""
    st.session_state.problem_code_key += 1


def get_topic_display_name(topic) -> str:
    """주제 한글 이름"""
    if isinstance(topic, str):
        topic_str = topic
    else:
        topic_str = topic.value if hasattr(topic, 'value') else str(topic)

    mapping = {
        "basics": "🔤 기초 문법",
        "data_structures": "📊 자료구조",
        "algorithms": "⚡ 알고리즘",
        "oop": "🏗️ 객체지향",
        "file_io": "📁 파일 입출력",
        "exceptions": "⚠️ 예외 처리",
        "modules": "📦 모듈/패키지",
        "functions": "🔧 함수",
    }

    if hasattr(topic, 'value'):
        return mapping.get(topic.value, topic.value)
    return mapping.get(topic_str, topic_str)


def get_difficulty_display_name(difficulty) -> str:
    """난이도 한글 이름"""
    if isinstance(difficulty, str):
        diff_str = difficulty
    else:
        diff_str = difficulty.value if hasattr(difficulty, 'value') else str(difficulty)

    mapping = {
        "beginner": "🌱 입문",
        "intermediate": "🌿 중급",
        "advanced": "🌳 고급",
        "expert": "🔥 전문가",
    }

    if hasattr(difficulty, 'value'):
        return mapping.get(difficulty.value, difficulty.value)
    return mapping.get(diff_str, diff_str)


def get_problem_type_display_name(problem_type) -> str:
    """문제 유형 한글 이름"""
    if isinstance(problem_type, str):
        pt_str = problem_type
    else:
        pt_str = problem_type.value if hasattr(problem_type, 'value') else str(problem_type)

    mapping = {
        "multiple_choice": "📝 객관식",
        "coding": "💻 코딩",
        "debugging": "🔍 디버깅",
        "algorithm": "🧮 알고리즘",
        "short_answer": "✏️ 단답형",
    }

    if hasattr(problem_type, 'value'):
        return mapping.get(problem_type.value, problem_type.value)
    return mapping.get(pt_str, pt_str)


def login_section():
    """로그인 섹션"""
    st.markdown("### 👤 사용자 설정")

    username = st.text_input(
        "닉네임을 입력하세요",
        value=st.session_state.username or "",
        placeholder="예: python_learner",
        key="username_input"
    )

    if st.button("시작하기", use_container_width=True):
        if username.strip():
            db = get_db_manager()
            user_id = db.get_or_create_user(username.strip())
            st.session_state.username = username.strip()
            st.session_state.user_id = user_id
            st.rerun()
        else:
            st.warning("닉네임을 입력해주세요.")


def sidebar():
    """사이드바 구성"""
    with st.sidebar:
        st.markdown("## 🐍 Python 교육 에이전트")
        st.markdown("---")

        # 사용자 정보
        if st.session_state.username:
            st.markdown(f"👤 **{st.session_state.username}**님 환영합니다!")
            if st.button("로그아웃", use_container_width=True):
                # 세션 상태 초기화
                st.session_state.username = None
                st.session_state.user_id = None
                st.session_state.chat_history = []
                st.session_state.current_problem = None
                st.session_state.problem_result = None
                st.session_state.problem_submitted = False
                st.rerun()
            st.markdown("---")

        # 모드 선택
        mode = st.radio(
            "📚 학습 모드",
            ["학습", "문제 풀기", "코드 리뷰", "대시보드"],
            index=["학습", "문제 풀기", "코드 리뷰", "대시보드"].index(st.session_state.mode),
        )
        st.session_state.mode = mode

        st.markdown("---")

        # 주제 선택
        topic_options = list(TopicCategory)
        topic_display = [get_topic_display_name(t) for t in topic_options]
        selected_topic_idx = st.selectbox(
            "📖 주제 선택",
            range(len(topic_options)),
            format_func=lambda x: topic_display[x],
        )
        selected_topic = topic_options[selected_topic_idx]

        # 난이도 선택
        difficulty_options = list(DifficultyLevel)
        difficulty_display = [get_difficulty_display_name(d) for d in difficulty_options]
        selected_difficulty_idx = st.selectbox(
            "📈 난이도 선택",
            range(len(difficulty_options)),
            format_func=lambda x: difficulty_display[x],
        )
        selected_difficulty = difficulty_options[selected_difficulty_idx]

        st.markdown("---")

        # 대화 초기화
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.current_problem = None
            st.session_state.hint_index = 0
            st.rerun()

        st.markdown("---")
        st.markdown("### ℹ️ 도움말")
        st.markdown("""
        - **학습 모드**: Python 개념을 질문하고 배워보세요
        - **문제 풀기**: 다양한 유형의 문제를 풀어보세요
        - **코드 리뷰**: 작성한 코드를 리뷰받아보세요
        - **대시보드**: 학습 통계를 확인하세요
        """)

        return selected_topic, selected_difficulty


def learning_mode(topic: TopicCategory, difficulty: DifficultyLevel):
    """학습 모드 UI"""
    st.markdown("## 🎓 학습 모드")
    st.markdown("Python 개념에 대해 질문해보세요!")

    # 채팅 히스토리 표시
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 사용자 입력
    user_input = st.chat_input("질문을 입력하세요...")

    if user_input:
        # 사용자 메시지 추가
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("생각하는 중..."):
                try:
                    teacher = get_teacher_agent()
                    response = teacher.teach_sync(
                        question=user_input,
                        topic=topic,
                        difficulty=difficulty,
                        chat_history=st.session_state.chat_history[:-1],
                    )
                    st.markdown(response)

                    # 응답 저장
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response,
                    })

                    # DB에 채팅 기록 저장
                    if st.session_state.user_id:
                        db = get_db_manager()
                        db.save_chat_message(
                            user_id=st.session_state.user_id,
                            role="user",
                            content=user_input,
                            topic=topic.value
                        )
                        db.save_chat_message(
                            user_id=st.session_state.user_id,
                            role="assistant",
                            content=response,
                            topic=topic.value
                        )
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {str(e)}")


def problem_mode(topic: TopicCategory, difficulty: DifficultyLevel):
    """문제 풀기 모드 UI"""
    st.markdown("## 📝 문제 풀기 모드")

    # 문제 유형 선택
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        problem_type_options = list(ProblemType)
        problem_type_display = [get_problem_type_display_name(p) for p in problem_type_options]
        selected_type_idx = st.selectbox(
            "문제 유형",
            range(len(problem_type_options)),
            format_func=lambda x: problem_type_display[x],
        )
        selected_problem_type = problem_type_options[selected_type_idx]

    with col2:
        if st.button("🎲 새 문제 생성", use_container_width=True):
            with st.spinner("문제 생성 중..."):
                try:
                    problem_agent = get_problem_agent()
                    problems = problem_agent.generate_problems_sync(
                        topic=topic,
                        difficulty=difficulty,
                        problem_type=selected_problem_type,
                        count=1,
                    )
                    if problems:
                        st.session_state.current_problem = problems[0]
                        st.session_state.hint_index = 0
                        # 이전 문제 풀이 상태 초기화
                        clear_problem_state()
                        st.rerun()
                    else:
                        st.error("문제 생성에 실패했습니다. 다시 시도해주세요.")
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {str(e)}")

    with col3:
        # 적응형 문제 출제 버튼
        if st.button("🎯 맞춤 문제", use_container_width=True, help="학습 이력 기반 맞춤형 문제 출제"):
            if st.session_state.user_id:
                with st.spinner("맞춤형 문제 생성 중..."):
                    try:
                        db = get_db_manager()
                        user_stats = db.get_user_statistics(st.session_state.user_id)
                        problem_agent = get_problem_agent()
                        problems = problem_agent.generate_adaptive_problem_sync(
                            user_stats=user_stats,
                            problem_type=selected_problem_type,
                        )
                        if problems:
                            st.session_state.current_problem = problems[0]
                            st.session_state.hint_index = 0
                            # 이전 문제 풀이 상태 초기화
                            clear_problem_state()
                            st.success("📊 학습 이력을 분석하여 맞춤형 문제를 생성했습니다!")
                            st.rerun()
                        else:
                            st.error("문제 생성에 실패했습니다. 다시 시도해주세요.")
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {str(e)}")
            else:
                st.warning("맞춤형 문제를 받으려면 먼저 로그인해주세요.")

    # 현재 문제 표시
    if st.session_state.current_problem:
        problem = st.session_state.current_problem

        st.markdown("---")
        st.markdown(f"**주제:** {get_topic_display_name(problem.topic)} | "
                    f"**난이도:** {get_difficulty_display_name(problem.difficulty)} | "
                    f"**유형:** {get_problem_type_display_name(problem.problem_type)}")

        # 문제 표시
        st.markdown('<div class="problem-box">', unsafe_allow_html=True)
        st.markdown(f"### 📋 문제")
        st.markdown(problem.question)
        st.markdown('</div>', unsafe_allow_html=True)

        # 객관식인 경우 선택지 표시
        if problem.options:
            st.markdown("### 선택지")
            user_answer = st.radio(
                "정답을 선택하세요:",
                problem.options,
                key="mc_answer",
            )

            # 이미 제출된 결과가 있으면 표시
            if st.session_state.problem_submitted and st.session_state.problem_result:
                result = st.session_state.problem_result
                if result.get("is_correct"):
                    st.success("🎉 정답입니다!")
                else:
                    st.error(f"❌ 오답입니다. 정답: {problem.answer}")
                st.markdown(f"**해설:** {problem.explanation}")
            elif st.button("정답 확인"):
                is_correct = user_answer == problem.answer
                score = 100 if is_correct else 0

                # 결과를 세션에 저장
                st.session_state.problem_result = {
                    "is_correct": is_correct,
                    "score": score,
                    "user_answer": user_answer,
                }
                st.session_state.problem_submitted = True

                if is_correct:
                    st.success("🎉 정답입니다!")
                else:
                    st.error(f"❌ 오답입니다. 정답: {problem.answer}")
                st.markdown(f"**해설:** {problem.explanation}")

                # DB에 저장
                if st.session_state.user_id:
                    db = get_db_manager()
                    db.save_problem_attempt(
                        user_id=st.session_state.user_id,
                        problem_type=problem.problem_type.value,
                        topic=problem.topic.value,
                        difficulty=problem.difficulty.value,
                        question=problem.question,
                        user_answer=user_answer,
                        correct_answer=problem.answer,
                        is_correct=is_correct,
                        score=score,
                        feedback=problem.explanation
                    )

        # 코딩/알고리즘 문제인 경우
        elif problem.problem_type in [ProblemType.CODING, ProblemType.ALGORITHM, ProblemType.DEBUGGING]:
            st.markdown("### 💻 코드 작성")

            # Ace 에디터 사용 (key 지원으로 입력 유지)
            default_code = "# 여기에 코드를 작성하세요\n\n"
            user_code = st_ace(
                value=st.session_state.get("code_answer", default_code),
                language="python",
                theme="monokai",
                height=300,
                key=f"ace_problem_{st.session_state.problem_code_key}",
                auto_update=True,
            )
            # 세션에 코드 저장
            if user_code:
                st.session_state.code_answer = user_code

            # 이미 제출된 결과가 있으면 표시
            if st.session_state.problem_submitted and st.session_state.problem_result:
                saved_result = st.session_state.problem_result
                if saved_result.get("is_correct"):
                    st.success(f"🎉 정답입니다! (점수: {saved_result.get('score', 0)}/100)")
                else:
                    st.warning(f"아쉽네요! (점수: {saved_result.get('score', 0)}/100)")

                st.markdown("### 📝 피드백")
                st.markdown(saved_result.get("feedback", ""))

                if saved_result.get("suggestions"):
                    st.markdown("### 💡 개선 제안")
                    for suggestion in saved_result["suggestions"]:
                        st.markdown(f"- {suggestion}")

                if saved_result.get("improved_code"):
                    st.markdown("### ✨ 개선된 코드")
                    st.code(saved_result["improved_code"], language="python")

                if saved_result.get("shown_answer"):
                    st.markdown("### ✅ 정답")
                    st.code(problem.answer, language="python")
                    st.markdown(f"**해설:** {problem.explanation}")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("제출하기", use_container_width=True):
                        if user_code.strip():
                            with st.spinner("코드 검토 중..."):
                                try:
                                    review_agent = get_review_agent()
                                    result = review_agent.review_submission_sync(
                                        code=user_code,
                                        problem=problem,
                                    )

                                    # 결과를 세션에 저장
                                    st.session_state.problem_result = {
                                        "is_correct": result.is_correct,
                                        "score": result.score,
                                        "feedback": result.feedback,
                                        "suggestions": result.suggestions,
                                        "improved_code": result.improved_code,
                                        "user_code": user_code,
                                        "shown_answer": False,
                                    }
                                    st.session_state.problem_submitted = True

                                    if result.is_correct:
                                        st.success(f"🎉 정답입니다! (점수: {result.score}/100)")
                                    else:
                                        st.warning(f"아쉽네요! (점수: {result.score}/100)")

                                    st.markdown("### 📝 피드백")
                                    st.markdown(result.feedback)

                                    if result.suggestions:
                                        st.markdown("### 💡 개선 제안")
                                        for suggestion in result.suggestions:
                                            st.markdown(f"- {suggestion}")

                                    if result.improved_code:
                                        st.markdown("### ✨ 개선된 코드")
                                        st.code(result.improved_code, language="python")

                                    # DB에 저장
                                    if st.session_state.user_id:
                                        db = get_db_manager()
                                        db.save_problem_attempt(
                                            user_id=st.session_state.user_id,
                                            problem_type=problem.problem_type.value,
                                            topic=problem.topic.value,
                                            difficulty=problem.difficulty.value,
                                            question=problem.question,
                                            user_answer=user_code,
                                            correct_answer=problem.answer,
                                            is_correct=result.is_correct,
                                            score=result.score,
                                            feedback=result.feedback
                                        )

                                except Exception as e:
                                    st.error(f"오류가 발생했습니다: {str(e)}")
                        else:
                            st.warning("코드를 입력해주세요.")

                with col2:
                    if st.button("정답 보기", use_container_width=True):
                        # 정답 보기 상태 저장
                        if st.session_state.problem_result is None:
                            st.session_state.problem_result = {}
                        st.session_state.problem_result["shown_answer"] = True
                        st.session_state.problem_submitted = True

                        st.markdown("### ✅ 정답")
                        st.code(problem.answer, language="python")
                        st.markdown(f"**해설:** {problem.explanation}")

        # 단답형인 경우
        else:
            user_answer = st.text_input("정답을 입력하세요:")

            # 이미 제출된 결과가 있으면 표시
            if st.session_state.problem_submitted and st.session_state.problem_result:
                saved_result = st.session_state.problem_result
                if saved_result.get("is_correct"):
                    st.success("🎉 정답입니다!")
                else:
                    st.error("❌ 오답입니다.")
                st.markdown(f"**정답:** {problem.answer}")
                st.markdown(f"**해설:** {problem.explanation}")
            elif st.button("정답 확인"):
                # 단순 비교 (실제로는 더 정교한 비교 필요)
                is_correct = user_answer.strip().lower() == problem.answer.strip().lower()
                score = 100 if is_correct else 0

                # 결과를 세션에 저장
                st.session_state.problem_result = {
                    "is_correct": is_correct,
                    "score": score,
                    "user_answer": user_answer,
                }
                st.session_state.problem_submitted = True

                if is_correct:
                    st.success("🎉 정답입니다!")
                else:
                    st.error("❌ 오답입니다.")
                st.markdown(f"**정답:** {problem.answer}")
                st.markdown(f"**해설:** {problem.explanation}")

                # DB에 저장
                if st.session_state.user_id:
                    db = get_db_manager()
                    db.save_problem_attempt(
                        user_id=st.session_state.user_id,
                        problem_type=problem.problem_type.value,
                        topic=problem.topic.value,
                        difficulty=problem.difficulty.value,
                        question=problem.question,
                        user_answer=user_answer,
                        correct_answer=problem.answer,
                        is_correct=is_correct,
                        score=score,
                        feedback=problem.explanation
                    )

        # 힌트 기능
        if problem.hints:
            st.markdown("---")
            st.markdown("### 💡 힌트")
            if st.button(f"힌트 보기 ({st.session_state.hint_index + 1}/{len(problem.hints)})"):
                if st.session_state.hint_index < len(problem.hints):
                    st.markdown(f'<div class="hint-box">{problem.hints[st.session_state.hint_index]}</div>',
                                unsafe_allow_html=True)
                    st.session_state.hint_index = min(
                        st.session_state.hint_index + 1,
                        len(problem.hints) - 1
                    )

    else:
        st.info("👆 '새 문제 생성' 버튼을 클릭하여 문제를 시작하세요!")


def review_mode():
    """코드 리뷰 모드 UI"""
    st.markdown("## 🔍 코드 리뷰 모드")
    st.markdown("작성한 Python 코드를 리뷰받아보세요!")

    # Ace 에디터 사용 (key 지원으로 입력 유지)
    default_review_code = "# 여기에 Python 코드를 입력하세요\n\ndef example():\n    pass\n"
    user_code = st_ace(
        value=st.session_state.get("review_code", default_review_code),
        language="python",
        theme="monokai",
        height=400,
        key="ace_review_code",
        auto_update=True,
    )
    # 세션에 코드 저장
    if user_code:
        st.session_state.review_code = user_code

    if st.button("🔍 코드 리뷰 받기", use_container_width=True):
        if user_code.strip():
            with st.spinner("코드 분석 중..."):
                try:
                    review_agent = get_review_agent()
                    result = review_agent.review_submission_sync(code=user_code)

                    # 점수 표시
                    score_color = "green" if result.score >= 70 else "orange" if result.score >= 40 else "red"
                    st.markdown(f"### 점수: :{score_color}[{result.score}/100]")

                    # 피드백
                    st.markdown("### 📝 전반적인 피드백")
                    st.markdown(result.feedback)

                    # 개선 제안
                    if result.suggestions:
                        st.markdown("### 💡 개선 제안")
                        for suggestion in result.suggestions:
                            st.markdown(f"- {suggestion}")

                    # 개선된 코드
                    if result.improved_code:
                        st.markdown("### ✨ 개선된 코드")
                        st.code(result.improved_code, language="python")

                except Exception as e:
                    st.error(f"오류가 발생했습니다: {str(e)}")
        else:
            st.warning("코드를 입력해주세요.")


def dashboard_mode():
    """대시보드 모드 UI"""
    st.markdown("## 📊 학습 대시보드")

    if not st.session_state.user_id:
        st.warning("대시보드를 보려면 먼저 닉네임을 입력해주세요.")
        return

    db = get_db_manager()
    stats = db.get_user_statistics(st.session_state.user_id)

    # 기본 통계 카드
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['total_attempts']}</div>
            <div class="stat-label">총 문제 풀이</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        accuracy = stats['accuracy']
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <div class="stat-number">{accuracy:.1f}%</div>
            <div class="stat-label">정답률</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        avg_score = stats['average_score']
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);">
            <div class="stat-number">{avg_score:.1f}</div>
            <div class="stat-label">평균 점수</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        topics_studied = len(stats['by_topic'])
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #4776E6 0%, #8E54E9 100%);">
            <div class="stat-number">{topics_studied}</div>
            <div class="stat-label">학습한 주제</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 상세 통계
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📚 주제별 성적")
        if stats['by_topic']:
            for topic_stat in stats['by_topic']:
                topic_name = get_topic_display_name(topic_stat['topic'])
                attempts = topic_stat['attempts']
                correct = topic_stat['correct'] or 0
                accuracy = (correct / attempts * 100) if attempts > 0 else 0
                avg = topic_stat['avg_score'] or 0

                st.markdown(f"**{topic_name}**")
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("풀이 수", attempts)
                col_b.metric("정답률", f"{accuracy:.1f}%")
                col_c.metric("평균 점수", f"{avg:.1f}")
                st.markdown("---")
        else:
            st.info("아직 풀이 기록이 없습니다.")

    with col2:
        st.markdown("### 📈 난이도별 성적")
        if stats['by_difficulty']:
            for diff_stat in stats['by_difficulty']:
                diff_name = get_difficulty_display_name(diff_stat['difficulty'])
                attempts = diff_stat['attempts']
                correct = diff_stat['correct'] or 0
                accuracy = (correct / attempts * 100) if attempts > 0 else 0
                avg = diff_stat['avg_score'] or 0

                st.markdown(f"**{diff_name}**")
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("풀이 수", attempts)
                col_b.metric("정답률", f"{accuracy:.1f}%")
                col_c.metric("평균 점수", f"{avg:.1f}")
                st.markdown("---")
        else:
            st.info("아직 풀이 기록이 없습니다.")

    # 취약 주제 및 추천 학습
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ⚠️ 취약 주제 (집중 학습 필요)")
        if stats['weak_topics']:
            for weak in stats['weak_topics']:
                topic_name = get_topic_display_name(weak['topic'])
                accuracy = weak['accuracy']
                st.markdown(f"""
                <div class="weak-topic">
                    <strong>{topic_name}</strong> - 정답률: {accuracy:.1f}% ({weak['attempts']}문제 풀이)
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("취약한 주제가 없습니다! 👏")

    with col2:
        st.markdown("### 📚 추천 학습 주제")
        problem_agent = get_problem_agent()
        recommendations = problem_agent.get_recommended_topics(stats)
        if recommendations:
            for rec in recommendations:
                topic_name = get_topic_display_name(rec['topic'])
                priority_icon = "🔴" if rec['priority'] == "high" else "🟡"
                st.markdown(f"""
                <div style="background-color: #e8f5e9; padding: 0.5rem 1rem; margin: 0.3rem 0; border-radius: 5px; border-left: 4px solid #4caf50;">
                    {priority_icon} <strong>{topic_name}</strong><br/>
                    <small>{rec['reason']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("모든 주제를 골고루 학습하셨습니다!")

    # 최근 활동
    st.markdown("### 📅 최근 7일 학습 활동")
    if stats['recent_activity']:
        dates = [r['date'] for r in stats['recent_activity']]
        attempts = [r['attempts'] for r in stats['recent_activity']]
        correct = [r['correct'] or 0 for r in stats['recent_activity']]

        import pandas as pd
        df = pd.DataFrame({
            '날짜': dates,
            '풀이 수': attempts,
            '정답 수': correct
        })
        st.bar_chart(df.set_index('날짜'))
    else:
        st.info("최근 7일간 학습 기록이 없습니다.")

    # 최근 풀이 기록
    st.markdown("### 📝 최근 풀이 기록")
    attempts = db.get_user_attempts(st.session_state.user_id, limit=10)
    if attempts:
        for attempt in attempts:
            status = "✅" if attempt['is_correct'] else "❌"
            topic_name = get_topic_display_name(attempt['topic'])
            diff_name = get_difficulty_display_name(attempt['difficulty'])
            type_name = get_problem_type_display_name(attempt['problem_type'])

            with st.expander(f"{status} {topic_name} | {diff_name} | {type_name} - 점수: {attempt['score']}"):
                st.markdown(f"**문제:** {attempt['question'][:200]}...")
                st.markdown(f"**제출 답안:** {attempt['user_answer'][:100]}...")
                st.markdown(f"**정답:** {attempt['correct_answer'][:100]}...")
                st.markdown(f"**풀이 시간:** {attempt['attempted_at']}")
    else:
        st.info("아직 풀이 기록이 없습니다.")


def main():
    """메인 함수"""
    init_session_state()

    # 로그인 체크
    if not st.session_state.username:
        st.markdown('<p class="main-header">🐍 Python 교육 에이전트</p>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: gray;">LangChain + RAG 기반 맞춤형 Python 학습 도우미</p>',
                    unsafe_allow_html=True)
        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_section()
        return

    # 사이드바
    topic, difficulty = sidebar()

    # 헤더
    st.markdown('<p class="main-header">🐍 Python 교육 에이전트</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: gray;">LangChain + RAG 기반 맞춤형 Python 학습 도우미</p>',
                unsafe_allow_html=True)
    st.markdown("---")

    # 모드별 UI
    if st.session_state.mode == "학습":
        learning_mode(topic, difficulty)
    elif st.session_state.mode == "문제 풀기":
        problem_mode(topic, difficulty)
    elif st.session_state.mode == "코드 리뷰":
        review_mode()
    else:
        dashboard_mode()


if __name__ == "__main__":
    main()
