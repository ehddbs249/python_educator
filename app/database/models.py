"""SQLite 데이터베이스 모델"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


# 데이터베이스 파일 경로
DB_PATH = Path(__file__).parent.parent.parent / "data" / "learning_history.db"


@dataclass
class User:
    """사용자 모델"""
    id: Optional[int] = None
    username: str = ""
    created_at: Optional[datetime] = None


@dataclass
class LearningSession:
    """학습 세션 모델"""
    id: Optional[int] = None
    user_id: int = 0
    topic: str = ""
    difficulty: str = ""
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


@dataclass
class ProblemAttempt:
    """문제 풀이 시도 모델"""
    id: Optional[int] = None
    user_id: int = 0
    session_id: Optional[int] = None
    problem_type: str = ""
    topic: str = ""
    difficulty: str = ""
    question: str = ""
    user_answer: str = ""
    correct_answer: str = ""
    is_correct: bool = False
    score: int = 0
    feedback: str = ""
    attempted_at: Optional[datetime] = None


@dataclass
class ChatHistory:
    """채팅 기록 모델"""
    id: Optional[int] = None
    user_id: int = 0
    session_id: Optional[int] = None
    role: str = ""  # "user" or "assistant"
    content: str = ""
    topic: str = ""
    created_at: Optional[datetime] = None


class DatabaseManager:
    """데이터베이스 관리자"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """데이터베이스 연결 반환"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """데이터베이스 테이블 초기화"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 사용자 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 학습 세션 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT,
                difficulty TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # 문제 풀이 시도 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS problem_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id INTEGER,
                problem_type TEXT NOT NULL,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                question TEXT NOT NULL,
                user_answer TEXT,
                correct_answer TEXT,
                is_correct BOOLEAN DEFAULT FALSE,
                score INTEGER DEFAULT 0,
                feedback TEXT,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (session_id) REFERENCES learning_sessions (id)
            )
        """)

        # 채팅 기록 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id INTEGER,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                topic TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (session_id) REFERENCES learning_sessions (id)
            )
        """)

        conn.commit()
        conn.close()

    # ========== 사용자 관련 ==========
    def create_user(self, username: str) -> int:
        """사용자 생성"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username) VALUES (?)",
                (username,)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # 이미 존재하는 사용자
            cursor.execute(
                "SELECT id FROM users WHERE username = ?",
                (username,)
            )
            return cursor.fetchone()["id"]
        finally:
            conn.close()

    def get_user(self, username: str) -> Optional[User]:
        """사용자 조회"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return User(
                id=row["id"],
                username=row["username"],
                created_at=row["created_at"]
            )
        return None

    def get_or_create_user(self, username: str) -> int:
        """사용자 조회 또는 생성"""
        user = self.get_user(username)
        if user:
            return user.id
        return self.create_user(username)

    # ========== 학습 세션 관련 ==========
    def create_session(self, user_id: int, topic: str, difficulty: str) -> int:
        """학습 세션 생성"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO learning_sessions (user_id, topic, difficulty)
               VALUES (?, ?, ?)""",
            (user_id, topic, difficulty)
        )
        conn.commit()
        session_id = cursor.lastrowid
        conn.close()
        return session_id

    def end_session(self, session_id: int):
        """학습 세션 종료"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE learning_sessions SET ended_at = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,)
        )
        conn.commit()
        conn.close()

    # ========== 문제 풀이 관련 ==========
    def save_problem_attempt(
        self,
        user_id: int,
        problem_type: str,
        topic: str,
        difficulty: str,
        question: str,
        user_answer: str,
        correct_answer: str,
        is_correct: bool,
        score: int,
        feedback: str = "",
        session_id: Optional[int] = None,
    ) -> int:
        """문제 풀이 시도 저장"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO problem_attempts
               (user_id, session_id, problem_type, topic, difficulty,
                question, user_answer, correct_answer, is_correct, score, feedback)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, session_id, problem_type, topic, difficulty,
             question, user_answer, correct_answer, is_correct, score, feedback)
        )
        conn.commit()
        attempt_id = cursor.lastrowid
        conn.close()
        return attempt_id

    def get_user_attempts(self, user_id: int, limit: int = 50) -> list[dict]:
        """사용자의 문제 풀이 기록 조회"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM problem_attempts
               WHERE user_id = ?
               ORDER BY attempted_at DESC
               LIMIT ?""",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # ========== 채팅 기록 관련 ==========
    def save_chat_message(
        self,
        user_id: int,
        role: str,
        content: str,
        topic: str = "",
        session_id: Optional[int] = None,
    ) -> int:
        """채팅 메시지 저장"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO chat_history
               (user_id, session_id, role, content, topic)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, session_id, role, content, topic)
        )
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        return message_id

    def get_chat_history(self, user_id: int, limit: int = 100) -> list[dict]:
        """채팅 기록 조회"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM chat_history
               WHERE user_id = ?
               ORDER BY created_at DESC
               LIMIT ?""",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # ========== 통계 관련 ==========
    def get_user_statistics(self, user_id: int) -> dict:
        """사용자 학습 통계 조회"""
        conn = self._get_connection()
        cursor = conn.cursor()

        stats = {}

        # 총 문제 풀이 수
        cursor.execute(
            "SELECT COUNT(*) as total FROM problem_attempts WHERE user_id = ?",
            (user_id,)
        )
        stats["total_attempts"] = cursor.fetchone()["total"]

        # 정답률
        cursor.execute(
            """SELECT
                COUNT(*) as total,
                SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct
               FROM problem_attempts WHERE user_id = ?""",
            (user_id,)
        )
        row = cursor.fetchone()
        total = row["total"] or 0
        correct = row["correct"] or 0
        stats["accuracy"] = (correct / total * 100) if total > 0 else 0

        # 평균 점수
        cursor.execute(
            "SELECT AVG(score) as avg_score FROM problem_attempts WHERE user_id = ?",
            (user_id,)
        )
        stats["average_score"] = cursor.fetchone()["avg_score"] or 0

        # 주제별 통계
        cursor.execute(
            """SELECT topic,
                COUNT(*) as attempts,
                SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct,
                AVG(score) as avg_score
               FROM problem_attempts
               WHERE user_id = ?
               GROUP BY topic""",
            (user_id,)
        )
        stats["by_topic"] = [dict(row) for row in cursor.fetchall()]

        # 난이도별 통계
        cursor.execute(
            """SELECT difficulty,
                COUNT(*) as attempts,
                SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct,
                AVG(score) as avg_score
               FROM problem_attempts
               WHERE user_id = ?
               GROUP BY difficulty""",
            (user_id,)
        )
        stats["by_difficulty"] = [dict(row) for row in cursor.fetchall()]

        # 문제 유형별 통계
        cursor.execute(
            """SELECT problem_type,
                COUNT(*) as attempts,
                SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct,
                AVG(score) as avg_score
               FROM problem_attempts
               WHERE user_id = ?
               GROUP BY problem_type""",
            (user_id,)
        )
        stats["by_problem_type"] = [dict(row) for row in cursor.fetchall()]

        # 최근 7일 학습 추이
        cursor.execute(
            """SELECT DATE(attempted_at) as date,
                COUNT(*) as attempts,
                SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct
               FROM problem_attempts
               WHERE user_id = ? AND attempted_at >= DATE('now', '-7 days')
               GROUP BY DATE(attempted_at)
               ORDER BY date""",
            (user_id,)
        )
        stats["recent_activity"] = [dict(row) for row in cursor.fetchall()]

        # 취약 주제 (정답률이 낮은 주제)
        cursor.execute(
            """SELECT topic,
                COUNT(*) as attempts,
                CAST(SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as accuracy
               FROM problem_attempts
               WHERE user_id = ?
               GROUP BY topic
               HAVING attempts >= 3
               ORDER BY accuracy ASC
               LIMIT 3""",
            (user_id,)
        )
        stats["weak_topics"] = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return stats


# 싱글톤 인스턴스
_db_manager = None


def get_db_manager() -> DatabaseManager:
    """DatabaseManager 싱글톤 인스턴스 반환"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
