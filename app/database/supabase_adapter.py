"""Supabase 데이터베이스 어댑터"""
from typing import Optional, Dict, List, Union
from datetime import datetime
import uuid
import os
from supabase import create_client, Client
from app.config import get_settings
from app.database.models import User, LearningSession, ProblemAttempt, ChatHistory


class SupabaseAdapter:
    """Supabase 데이터베이스 어댑터"""

    def __init__(self):
        settings = get_settings()
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )

    def _convert_to_uuid(self, value: Union[str, int, None]) -> Optional[str]:
        """ID를 UUID 문자열로 변환"""
        if value is None:
            return None
        if isinstance(value, int):
            # SQLite에서 마이그레이션하는 경우, int ID를 UUID로 변환
            return str(uuid.UUID(int=value))
        return str(value)

    def _handle_error(self, response):
        """Supabase 응답 에러 처리"""
        if hasattr(response, 'data') and response.data is None:
            if hasattr(response, 'error') and response.error:
                raise Exception(f"Database error: {response.error}")
        return response

    # ========== 사용자 관련 ==========
    def create_user(self, username: str) -> str:
        """사용자 생성 (UUID 반환)"""
        try:
            response = self.supabase.table("users").insert({
                "username": username
            }).execute()
            self._handle_error(response)
            return response.data[0]["id"]
        except Exception as e:
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                # 이미 존재하는 사용자 조회
                response = self.supabase.table("users").select("id").eq("username", username).execute()
                self._handle_error(response)
                if response.data:
                    return response.data[0]["id"]
            raise e

    def get_user(self, username: str) -> Optional[User]:
        """사용자 조회"""
        response = self.supabase.table("users").select("*").eq("username", username).execute()
        self._handle_error(response)

        if response.data:
            row = response.data[0]
            return User(
                id=row["id"],
                username=row["username"],
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
            )
        return None

    def get_or_create_user(self, username: str) -> str:
        """사용자 조회 또는 생성"""
        user = self.get_user(username)
        if user:
            return user.id
        return self.create_user(username)

    # ========== 학습 세션 관련 ==========
    def create_session(self, user_id: str, topic: str, difficulty: str) -> str:
        """학습 세션 생성"""
        response = self.supabase.table("learning_sessions").insert({
            "user_id": user_id,
            "topic": topic,
            "difficulty": difficulty
        }).execute()
        self._handle_error(response)
        return response.data[0]["id"]

    def end_session(self, session_id: str):
        """학습 세션 종료"""
        response = self.supabase.table("learning_sessions").update({
            "ended_at": datetime.utcnow().isoformat()
        }).eq("id", session_id).execute()
        self._handle_error(response)

    # ========== 문제 풀이 관련 ==========
    def save_problem_attempt(
        self,
        user_id: str,
        problem_type: str,
        topic: str,
        difficulty: str,
        question: str,
        user_answer: str,
        correct_answer: str,
        is_correct: bool,
        score: int,
        feedback: str = "",
        session_id: Optional[str] = None,
    ) -> str:
        """문제 풀이 시도 저장"""
        response = self.supabase.table("problem_attempts").insert({
            "user_id": user_id,
            "session_id": session_id,
            "problem_type": problem_type,
            "topic": topic,
            "difficulty": difficulty,
            "question": question,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "score": score,
            "feedback": feedback
        }).execute()
        self._handle_error(response)
        return response.data[0]["id"]

    def get_user_attempts(self, user_id: str, limit: int = 50) -> List[Dict]:
        """사용자의 문제 풀이 기록 조회"""
        response = self.supabase.table("problem_attempts").select("*").eq(
            "user_id", user_id
        ).order("attempted_at", desc=True).limit(limit).execute()
        self._handle_error(response)
        return response.data

    # ========== 채팅 기록 관련 ==========
    def save_chat_message(
        self,
        user_id: str,
        role: str,
        content: str,
        topic: str = "",
        session_id: Optional[str] = None,
    ) -> str:
        """채팅 메시지 저장"""
        response = self.supabase.table("chat_history").insert({
            "user_id": user_id,
            "session_id": session_id,
            "role": role,
            "content": content,
            "topic": topic
        }).execute()
        self._handle_error(response)
        return response.data[0]["id"]

    def get_chat_history(self, user_id: str, limit: int = 100) -> List[Dict]:
        """채팅 기록 조회"""
        response = self.supabase.table("chat_history").select("*").eq(
            "user_id", user_id
        ).order("created_at", desc=True).limit(limit).execute()
        self._handle_error(response)
        return response.data

    # ========== 통계 관련 ==========
    def get_user_statistics(self, user_id: str) -> Dict:
        """사용자 학습 통계 조회"""
        stats = {}

        # 총 문제 풀이 수
        response = self.supabase.table("problem_attempts").select(
            "id", count="exact"
        ).eq("user_id", user_id).execute()
        self._handle_error(response)
        stats["total_attempts"] = response.count or 0

        # 정답률 계산을 위한 데이터
        response = self.supabase.table("problem_attempts").select(
            "is_correct"
        ).eq("user_id", user_id).execute()
        self._handle_error(response)

        attempts = response.data
        total = len(attempts)
        correct = sum(1 for attempt in attempts if attempt["is_correct"])
        stats["accuracy"] = (correct / total * 100) if total > 0 else 0

        # 평균 점수
        response = self.supabase.rpc("get_avg_score", {
            "p_user_id": user_id
        }).execute()
        stats["average_score"] = response.data or 0

        # 주제별 통계
        response = self.supabase.rpc("get_topic_stats", {
            "p_user_id": user_id
        }).execute()
        stats["by_topic"] = response.data or []

        # 난이도별 통계
        response = self.supabase.rpc("get_difficulty_stats", {
            "p_user_id": user_id
        }).execute()
        stats["by_difficulty"] = response.data or []

        # 문제 유형별 통계
        response = self.supabase.rpc("get_problem_type_stats", {
            "p_user_id": user_id
        }).execute()
        stats["by_problem_type"] = response.data or []

        # 최근 7일 활동
        response = self.supabase.rpc("get_recent_activity", {
            "p_user_id": user_id
        }).execute()
        stats["recent_activity"] = response.data or []

        # 취약 주제
        response = self.supabase.rpc("get_weak_topics", {
            "p_user_id": user_id
        }).execute()
        stats["weak_topics"] = response.data or []

        return stats


# 싱글톤 인스턴스
_supabase_adapter = None


def get_supabase_adapter() -> SupabaseAdapter:
    """SupabaseAdapter 싱글톤 인스턴스 반환"""
    global _supabase_adapter
    if _supabase_adapter is None:
        _supabase_adapter = SupabaseAdapter()
    return _supabase_adapter