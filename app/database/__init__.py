"""Database module"""
from app.database.models import (
    DatabaseManager,
    User,
    LearningSession,
    ProblemAttempt,
    ChatHistory,
)
from app.database.supabase_adapter import (
    SupabaseAdapter,
    get_supabase_adapter,
)
from app.config import get_settings

def get_db_manager():
    """데이터베이스 매니저 반환 (설정에 따라 SQLite 또는 Supabase)"""
    settings = get_settings()

    if settings.database_provider == "supabase":
        return get_supabase_adapter()
    else:
        # SQLite 기본값
        from app.database.models import get_db_manager as get_sqlite_manager
        return get_sqlite_manager()

__all__ = [
    "DatabaseManager",
    "SupabaseAdapter",
    "get_db_manager",
    "get_supabase_adapter",
    "User",
    "LearningSession",
    "ProblemAttempt",
    "ChatHistory",
]
