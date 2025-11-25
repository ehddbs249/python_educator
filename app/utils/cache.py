"""캐싱 유틸리티"""
import functools
import hashlib
import json
import time
from typing import Any, Callable, Dict, Optional
import streamlit as st
from pathlib import Path


class FileCache:
    """파일 기반 캐시"""

    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """캐시 키 생성"""
        key_data = {
            "func": func_name,
            "args": str(args),
            "kwargs": str(sorted(kwargs.items())),
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, key: str, max_age: int = 3600) -> Optional[Any]:
        """캐시에서 값 조회"""
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 만료 시간 확인
            if time.time() - cache_data.get("timestamp", 0) > max_age:
                cache_file.unlink(missing_ok=True)
                return None

            return cache_data.get("value")

        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            cache_file.unlink(missing_ok=True)
            return None

    def set(self, key: str, value: Any) -> None:
        """캐시에 값 저장"""
        cache_file = self.cache_dir / f"{key}.json"

        cache_data = {
            "value": value,
            "timestamp": time.time(),
        }

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, default=str)
        except Exception:
            # 직렬화 실패 시 무시
            pass

    def clear(self) -> None:
        """캐시 초기화"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink(missing_ok=True)


# 전역 캐시 인스턴스
_file_cache = FileCache()


def cached(max_age: int = 3600, use_streamlit_cache: bool = True):
    """캐싱 데코레이터

    Args:
        max_age: 캐시 유효 시간 (초)
        use_streamlit_cache: Streamlit 캐시 사용 여부
    """

    def decorator(func: Callable) -> Callable:
        if use_streamlit_cache:
            # Streamlit 캐시 사용
            @st.cache_data(ttl=max_age)
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

        else:
            # 파일 캐시 사용
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = _file_cache._get_cache_key(
                    func.__name__, args, kwargs
                )

                # 캐시에서 조회
                cached_value = _file_cache.get(cache_key, max_age)
                if cached_value is not None:
                    return cached_value

                # 함수 실행 및 캐시 저장
                result = func(*args, **kwargs)
                _file_cache.set(cache_key, result)
                return result

        return wrapper

    return decorator


def clear_cache():
    """모든 캐시 초기화"""
    # Streamlit 캐시 초기화
    st.cache_data.clear()

    # 파일 캐시 초기화
    _file_cache.clear()


@cached(max_age=1800)  # 30분 캐시
def get_problem_generation_cache(topic: str, difficulty: str, problem_type: str) -> Optional[Dict]:
    """문제 생성 캐시"""
    # 이 함수는 실제 문제 생성 함수에서 사용
    return None


@cached(max_age=3600)  # 1시간 캐시
def get_user_statistics_cache(user_id: str) -> Optional[Dict]:
    """사용자 통계 캐시"""
    # 이 함수는 실제 통계 조회 함수에서 사용
    return None


@cached(max_age=7200)  # 2시간 캐시
def get_vectorstore_search_cache(query: str) -> Optional[list]:
    """벡터 검색 캐시"""
    # 이 함수는 실제 벡터 검색 함수에서 사용
    return None


# 성능 모니터링 데코레이터
def monitor_performance(func: Callable) -> Callable:
    """함수 실행 시간 모니터링"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        execution_time = end_time - start_time

        # 개발 모드에서만 로깅
        if st.secrets.get("DEBUG", False):
            st.sidebar.metric(
                f"⏱️ {func.__name__}",
                f"{execution_time:.2f}s"
            )

        return result

    return wrapper


# 메모리 사용량 최적화 유틸리티
def optimize_dataframe_memory(df):
    """DataFrame 메모리 사용량 최적화"""
    try:
        import pandas as pd

        for col in df.columns:
            col_type = df[col].dtype

            if col_type != object:
                c_min = df[col].min()
                c_max = df[col].max()

                if str(col_type)[:3] == 'int':
                    if c_min > pd.np.iinfo(pd.np.int8).min and c_max < pd.np.iinfo(pd.np.int8).max:
                        df[col] = df[col].astype(pd.np.int8)
                    elif c_min > pd.np.iinfo(pd.np.int16).min and c_max < pd.np.iinfo(pd.np.int16).max:
                        df[col] = df[col].astype(pd.np.int16)
                    elif c_min > pd.np.iinfo(pd.np.int32).min and c_max < pd.np.iinfo(pd.np.int32).max:
                        df[col] = df[col].astype(pd.np.int32)

                else:
                    if c_min > pd.np.finfo(pd.np.float16).min and c_max < pd.np.finfo(pd.np.float16).max:
                        df[col] = df[col].astype(pd.np.float32)

    except Exception:
        # pandas 없으면 무시
        pass

    return df