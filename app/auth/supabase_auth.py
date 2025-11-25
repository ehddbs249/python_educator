"""Supabase Auth 인증 시스템"""
import streamlit as st
from typing import Optional, Dict, Any
from supabase import Client
from app.config import get_settings
from app.database.supabase_adapter import get_supabase_adapter


class SupabaseAuthManager:
    """Supabase Authentication 관리자"""

    def __init__(self):
        self.settings = get_settings()
        self.supabase: Client = get_supabase_adapter().supabase

    def sign_up(self, email: str, password: str, username: str) -> Dict[str, Any]:
        """사용자 회원가입"""
        try:
            # Supabase Auth 회원가입
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "username": username,
                        "display_name": username
                    }
                }
            })

            if response.user:
                # 프로필 테이블에 추가 정보 저장
                self.supabase.table("users").insert({
                    "id": response.user.id,
                    "username": username,
                    "email": email
                }).execute()

                return {
                    "success": True,
                    "user": response.user,
                    "message": "회원가입이 완료되었습니다. 이메일을 확인하세요."
                }
            else:
                return {
                    "success": False,
                    "error": "회원가입에 실패했습니다.",
                    "message": "다시 시도해주세요."
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "회원가입 중 오류가 발생했습니다."
            }

    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """사용자 로그인"""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user:
                # 사용자 프로필 정보 조회
                profile = self.supabase.table("users").select("*").eq(
                    "id", response.user.id
                ).execute()

                user_data = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "username": profile.data[0]["username"] if profile.data else email.split("@")[0]
                }

                return {
                    "success": True,
                    "user": user_data,
                    "session": response.session,
                    "message": "로그인 성공"
                }
            else:
                return {
                    "success": False,
                    "error": "로그인 실패",
                    "message": "이메일 또는 비밀번호를 확인하세요."
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "로그인 중 오류가 발생했습니다."
            }

    def sign_out(self) -> bool:
        """로그아웃"""
        try:
            self.supabase.auth.sign_out()
            return True
        except Exception:
            return False

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """현재 로그인된 사용자 정보 조회"""
        try:
            user = self.supabase.auth.get_user()
            if user:
                return {
                    "id": user.user.id,
                    "email": user.user.email,
                    "user_metadata": user.user.user_metadata
                }
            return None
        except Exception:
            return None

    def reset_password(self, email: str) -> Dict[str, Any]:
        """비밀번호 재설정"""
        try:
            response = self.supabase.auth.reset_password_email(email)
            return {
                "success": True,
                "message": "비밀번호 재설정 이메일을 보냈습니다."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "비밀번호 재설정에 실패했습니다."
            }

    def update_password(self, new_password: str) -> Dict[str, Any]:
        """비밀번호 변경"""
        try:
            response = self.supabase.auth.update_user({
                "password": new_password
            })

            if response.user:
                return {
                    "success": True,
                    "message": "비밀번호가 변경되었습니다."
                }
            else:
                return {
                    "success": False,
                    "message": "비밀번호 변경에 실패했습니다."
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "비밀번호 변경 중 오류가 발생했습니다."
            }

    def update_profile(self, username: str, display_name: str = None) -> Dict[str, Any]:
        """프로필 업데이트"""
        try:
            user = self.get_current_user()
            if not user:
                return {
                    "success": False,
                    "message": "로그인이 필요합니다."
                }

            # users 테이블 업데이트
            self.supabase.table("users").update({
                "username": username,
                "display_name": display_name or username
            }).eq("id", user["id"]).execute()

            # Auth 메타데이터 업데이트
            self.supabase.auth.update_user({
                "data": {
                    "username": username,
                    "display_name": display_name or username
                }
            })

            return {
                "success": True,
                "message": "프로필이 업데이트되었습니다."
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "프로필 업데이트 중 오류가 발생했습니다."
            }


# 싱글톤 인스턴스
_auth_manager = None


def get_auth_manager() -> SupabaseAuthManager:
    """SupabaseAuthManager 싱글톤 인스턴스 반환"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = SupabaseAuthManager()
    return _auth_manager


# Streamlit용 인증 헬퍼 함수들
def init_auth_state():
    """Streamlit 세션에 인증 상태 초기화"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "auth_session" not in st.session_state:
        st.session_state.auth_session = None


def require_auth(func):
    """인증이 필요한 함수 데코레이터"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get("authenticated", False):
            st.error("로그인이 필요합니다.")
            show_auth_form()
            st.stop()
        return func(*args, **kwargs)
    return wrapper


def show_auth_form():
    """로그인/회원가입 폼 표시"""
    auth_manager = get_auth_manager()

    st.markdown("### 🔐 인증")

    tab1, tab2 = st.tabs(["로그인", "회원가입"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("이메일", key="login_email")
            password = st.text_input("비밀번호", type="password", key="login_password")
            login_btn = st.form_submit_button("로그인")

            if login_btn:
                if email and password:
                    result = auth_manager.sign_in(email, password)

                    if result["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user = result["user"]
                        st.session_state.auth_session = result["session"]
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])
                else:
                    st.warning("이메일과 비밀번호를 입력하세요.")

    with tab2:
        with st.form("signup_form"):
            email = st.text_input("이메일", key="signup_email")
            username = st.text_input("사용자명", key="signup_username")
            password = st.text_input("비밀번호", type="password", key="signup_password")
            confirm_password = st.text_input("비밀번호 확인", type="password", key="confirm_password")
            signup_btn = st.form_submit_button("회원가입")

            if signup_btn:
                if email and username and password:
                    if password == confirm_password:
                        result = auth_manager.sign_up(email, password, username)

                        if result["success"]:
                            st.success(result["message"])
                        else:
                            st.error(result["message"])
                    else:
                        st.error("비밀번호가 일치하지 않습니다.")
                else:
                    st.warning("모든 필드를 입력하세요.")

    # 비밀번호 재설정
    with st.expander("비밀번호를 잊으셨나요?"):
        reset_email = st.text_input("이메일 주소", key="reset_email")
        if st.button("비밀번호 재설정"):
            if reset_email:
                result = auth_manager.reset_password(reset_email)
                if result["success"]:
                    st.success(result["message"])
                else:
                    st.error(result["message"])


def show_user_profile():
    """사용자 프로필 표시"""
    if not st.session_state.get("authenticated", False):
        return

    user = st.session_state.user
    auth_manager = get_auth_manager()

    st.sidebar.markdown(f"👤 **{user['username']}**")
    st.sidebar.markdown(f"✉️ {user['email']}")

    with st.sidebar.expander("프로필 설정"):
        with st.form("profile_form"):
            new_username = st.text_input("사용자명", value=user['username'])
            update_btn = st.form_submit_button("프로필 업데이트")

            if update_btn:
                result = auth_manager.update_profile(new_username)
                if result["success"]:
                    st.session_state.user['username'] = new_username
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result["message"])

    # 로그아웃 버튼
    if st.sidebar.button("로그아웃"):
        auth_manager.sign_out()
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.auth_session = None
        st.rerun()