"""Supabase 연결 테스트"""
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.config import get_settings
from supabase import create_client

def test_connection():
    """Supabase 연결 테스트"""
    try:
        settings = get_settings()
        print(f"🔗 Supabase URL: {settings.supabase_url}")
        print(f"🔑 API Key: {settings.supabase_key[:20]}...")

        # Supabase 클라이언트 생성
        supabase = create_client(settings.supabase_url, settings.supabase_key)
        print("✅ Supabase 클라이언트 생성 성공")

        # 간단한 쿼리 테스트 (ping)
        response = supabase.table('users').select('*').limit(1).execute()
        print(f"✅ Supabase 연결 테스트 성공: {len(response.data)}개 사용자")

        return True

    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        return False

if __name__ == "__main__":
    print("=== Supabase 연결 테스트 ===")
    success = test_connection()

    if success:
        print("\n🎉 Supabase 연결이 정상적으로 작동합니다!")
    else:
        print("\n💥 연결에 문제가 있습니다. 설정을 확인하세요.")