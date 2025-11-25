"""SQLite에서 Supabase로 데이터 마이그레이션 스크립트"""
import os
import sys
from pathlib import Path
import sqlite3
from datetime import datetime
from uuid import uuid4

# 프로젝트 루트를 path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database.models import DatabaseManager as SQLiteManager
from app.database.supabase_adapter import SupabaseAdapter
from app.config import get_settings


def migrate_data():
    """SQLite에서 Supabase로 데이터 마이그레이션"""

    # 환경변수 확인
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_key:
        print("❌ Supabase 설정이 필요합니다. .env 파일을 확인하세요.")
        print("SUPABASE_URL과 SUPABASE_KEY를 설정해주세요.")
        return False

    try:
        # 데이터베이스 매니저 초기화
        sqlite_db = SQLiteManager()
        supabase_db = SupabaseAdapter()

        print("🚀 SQLite에서 Supabase로 데이터 마이그레이션 시작...")

        # SQLite 연결
        conn = sqlite_db._get_connection()
        cursor = conn.cursor()

        # 1. 사용자 마이그레이션
        print("👤 사용자 데이터 마이그레이션 중...")
        cursor.execute("SELECT * FROM users ORDER BY created_at")
        users = cursor.fetchall()

        user_id_mapping = {}  # SQLite ID -> Supabase UUID 매핑

        for user in users:
            try:
                supabase_user_id = supabase_db.create_user(user["username"])
                user_id_mapping[user["id"]] = supabase_user_id
                print(f"  ✓ 사용자 '{user['username']}' 마이그레이션 완료")
            except Exception as e:
                print(f"  ❌ 사용자 '{user['username']}' 마이그레이션 실패: {e}")

        print(f"✅ 사용자 마이그레이션 완료: {len(user_id_mapping)}명")

        # 2. 학습 세션 마이그레이션
        print("📚 학습 세션 데이터 마이그레이션 중...")
        cursor.execute("SELECT * FROM learning_sessions ORDER BY started_at")
        sessions = cursor.fetchall()

        session_id_mapping = {}  # SQLite ID -> Supabase UUID 매핑

        for session in sessions:
            if session["user_id"] not in user_id_mapping:
                print(f"  ⚠️ 세션 {session['id']}: 사용자 {session['user_id']} 찾을 수 없음")
                continue

            try:
                supabase_session_id = supabase_db.create_session(
                    user_id=user_id_mapping[session["user_id"]],
                    topic=session["topic"] or "",
                    difficulty=session["difficulty"] or ""
                )
                session_id_mapping[session["id"]] = supabase_session_id

                # 종료 시간이 있으면 업데이트
                if session["ended_at"]:
                    supabase_db.end_session(supabase_session_id)

                print(f"  ✓ 세션 {session['id']} 마이그레이션 완료")
            except Exception as e:
                print(f"  ❌ 세션 {session['id']} 마이그레이션 실패: {e}")

        print(f"✅ 학습 세션 마이그레이션 완료: {len(session_id_mapping)}개")

        # 3. 문제 풀이 기록 마이그레이션
        print("📝 문제 풀이 기록 마이그레이션 중...")
        cursor.execute("SELECT * FROM problem_attempts ORDER BY attempted_at")
        attempts = cursor.fetchall()

        migrated_attempts = 0
        for attempt in attempts:
            if attempt["user_id"] not in user_id_mapping:
                print(f"  ⚠️ 시도 {attempt['id']}: 사용자 {attempt['user_id']} 찾을 수 없음")
                continue

            try:
                session_id = None
                if attempt["session_id"] and attempt["session_id"] in session_id_mapping:
                    session_id = session_id_mapping[attempt["session_id"]]

                supabase_db.save_problem_attempt(
                    user_id=user_id_mapping[attempt["user_id"]],
                    problem_type=attempt["problem_type"],
                    topic=attempt["topic"],
                    difficulty=attempt["difficulty"],
                    question=attempt["question"],
                    user_answer=attempt["user_answer"] or "",
                    correct_answer=attempt["correct_answer"] or "",
                    is_correct=bool(attempt["is_correct"]),
                    score=attempt["score"],
                    feedback=attempt["feedback"] or "",
                    session_id=session_id
                )
                migrated_attempts += 1

                if migrated_attempts % 10 == 0:
                    print(f"  📊 {migrated_attempts}개 기록 마이그레이션 완료...")

            except Exception as e:
                print(f"  ❌ 시도 {attempt['id']} 마이그레이션 실패: {e}")

        print(f"✅ 문제 풀이 기록 마이그레이션 완료: {migrated_attempts}개")

        # 4. 채팅 기록 마이그레이션
        print("💬 채팅 기록 마이그레이션 중...")
        cursor.execute("SELECT * FROM chat_history ORDER BY created_at")
        chats = cursor.fetchall()

        migrated_chats = 0
        for chat in chats:
            if chat["user_id"] not in user_id_mapping:
                print(f"  ⚠️ 채팅 {chat['id']}: 사용자 {chat['user_id']} 찾을 수 없음")
                continue

            try:
                session_id = None
                if chat["session_id"] and chat["session_id"] in session_id_mapping:
                    session_id = session_id_mapping[chat["session_id"]]

                supabase_db.save_chat_message(
                    user_id=user_id_mapping[chat["user_id"]],
                    role=chat["role"],
                    content=chat["content"],
                    topic=chat["topic"] or "",
                    session_id=session_id
                )
                migrated_chats += 1

                if migrated_chats % 50 == 0:
                    print(f"  💭 {migrated_chats}개 채팅 마이그레이션 완료...")

            except Exception as e:
                print(f"  ❌ 채팅 {chat['id']} 마이그레이션 실패: {e}")

        print(f"✅ 채팅 기록 마이그레이션 완료: {migrated_chats}개")

        conn.close()

        print("🎉 마이그레이션 완료!")
        print(f"📊 요약:")
        print(f"  - 사용자: {len(user_id_mapping)}명")
        print(f"  - 학습 세션: {len(session_id_mapping)}개")
        print(f"  - 문제 풀이: {migrated_attempts}개")
        print(f"  - 채팅 기록: {migrated_chats}개")

        return True

    except Exception as e:
        print(f"❌ 마이그레이션 중 오류 발생: {e}")
        return False


if __name__ == "__main__":
    print("=== SQLite to Supabase 마이그레이션 ===")
    print()

    # .env 파일 확인
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env 파일이 없습니다. .env.example을 복사하여 .env를 만들고 Supabase 설정을 추가하세요.")
        sys.exit(1)

    # 마이그레이션 실행
    success = migrate_data()

    if success:
        print()
        print("✅ 마이그레이션이 완료되었습니다!")
        print("이제 .env 파일에서 DATABASE_PROVIDER=supabase로 변경하여 Supabase를 사용할 수 있습니다.")
    else:
        print()
        print("❌ 마이그레이션이 실패했습니다. 위의 에러 메시지를 확인하세요.")
        sys.exit(1)