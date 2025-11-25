-- Python 교육 에이전트 Supabase 스키마
-- 이 SQL을 Supabase SQL Editor에서 실행하세요

-- 1. 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 학습 세션 테이블
CREATE TABLE IF NOT EXISTS learning_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic TEXT,
    difficulty TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE
);

-- 3. 문제 풀이 시도 테이블
CREATE TABLE IF NOT EXISTS problem_attempts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES learning_sessions(id) ON DELETE SET NULL,
    problem_type TEXT NOT NULL,
    topic TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    question TEXT NOT NULL,
    user_answer TEXT,
    correct_answer TEXT,
    is_correct BOOLEAN DEFAULT FALSE,
    score INTEGER DEFAULT 0,
    feedback TEXT,
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 채팅 기록 테이블
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES learning_sessions(id) ON DELETE SET NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    topic TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_problem_attempts_user_id ON problem_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_problem_attempts_topic ON problem_attempts(topic);
CREATE INDEX IF NOT EXISTS idx_problem_attempts_attempted_at ON problem_attempts(attempted_at);
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history(created_at);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_user_id ON learning_sessions(user_id);

-- Row Level Security (RLS) 활성화
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE problem_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

-- RLS 정책 (사용자는 자신의 데이터만 접근 가능)
-- 익명 사용자도 접근 가능하도록 설정 (교육 앱 특성상)

-- 사용자 테이블 정책
CREATE POLICY "Users can view and insert their own data" ON users
    FOR ALL USING (true);

-- 학습 세션 정책
CREATE POLICY "Users can manage their own sessions" ON learning_sessions
    FOR ALL USING (true);

-- 문제 시도 정책
CREATE POLICY "Users can manage their own attempts" ON problem_attempts
    FOR ALL USING (true);

-- 채팅 기록 정책
CREATE POLICY "Users can manage their own chat history" ON chat_history
    FOR ALL USING (true);

-- ==========================================
-- RPC 함수들 (통계 계산용)
-- ==========================================

-- 평균 점수 계산
CREATE OR REPLACE FUNCTION get_avg_score(p_user_id UUID)
RETURNS NUMERIC
LANGUAGE SQL
SECURITY DEFINER
AS $$
    SELECT COALESCE(AVG(score), 0)::NUMERIC
    FROM problem_attempts
    WHERE user_id = p_user_id;
$$;

-- 주제별 통계
CREATE OR REPLACE FUNCTION get_topic_stats(p_user_id UUID)
RETURNS TABLE (
    topic TEXT,
    attempts BIGINT,
    correct BIGINT,
    avg_score NUMERIC
)
LANGUAGE SQL
SECURITY DEFINER
AS $$
    SELECT
        t.topic,
        COUNT(*) as attempts,
        SUM(CASE WHEN t.is_correct THEN 1 ELSE 0 END) as correct,
        AVG(t.score)::NUMERIC as avg_score
    FROM problem_attempts t
    WHERE t.user_id = p_user_id
    GROUP BY t.topic;
$$;

-- 난이도별 통계
CREATE OR REPLACE FUNCTION get_difficulty_stats(p_user_id UUID)
RETURNS TABLE (
    difficulty TEXT,
    attempts BIGINT,
    correct BIGINT,
    avg_score NUMERIC
)
LANGUAGE SQL
SECURITY DEFINER
AS $$
    SELECT
        d.difficulty,
        COUNT(*) as attempts,
        SUM(CASE WHEN d.is_correct THEN 1 ELSE 0 END) as correct,
        AVG(d.score)::NUMERIC as avg_score
    FROM problem_attempts d
    WHERE d.user_id = p_user_id
    GROUP BY d.difficulty;
$$;

-- 문제 유형별 통계
CREATE OR REPLACE FUNCTION get_problem_type_stats(p_user_id UUID)
RETURNS TABLE (
    problem_type TEXT,
    attempts BIGINT,
    correct BIGINT,
    avg_score NUMERIC
)
LANGUAGE SQL
SECURITY DEFINER
AS $$
    SELECT
        pt.problem_type,
        COUNT(*) as attempts,
        SUM(CASE WHEN pt.is_correct THEN 1 ELSE 0 END) as correct,
        AVG(pt.score)::NUMERIC as avg_score
    FROM problem_attempts pt
    WHERE pt.user_id = p_user_id
    GROUP BY pt.problem_type;
$$;

-- 최근 7일 활동
CREATE OR REPLACE FUNCTION get_recent_activity(p_user_id UUID)
RETURNS TABLE (
    date DATE,
    attempts BIGINT,
    correct BIGINT
)
LANGUAGE SQL
SECURITY DEFINER
AS $$
    SELECT
        ra.attempted_at::DATE as date,
        COUNT(*) as attempts,
        SUM(CASE WHEN ra.is_correct THEN 1 ELSE 0 END) as correct
    FROM problem_attempts ra
    WHERE ra.user_id = p_user_id
        AND ra.attempted_at >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY ra.attempted_at::DATE
    ORDER BY date;
$$;

-- 취약 주제 (정답률이 낮은 주제)
CREATE OR REPLACE FUNCTION get_weak_topics(p_user_id UUID)
RETURNS TABLE (
    topic TEXT,
    attempts BIGINT,
    accuracy NUMERIC
)
LANGUAGE SQL
SECURITY DEFINER
AS $$
    SELECT
        wt.topic,
        COUNT(*) as attempts,
        (SUM(CASE WHEN wt.is_correct THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100) as accuracy
    FROM problem_attempts wt
    WHERE wt.user_id = p_user_id
    GROUP BY wt.topic
    HAVING COUNT(*) >= 3
    ORDER BY accuracy ASC
    LIMIT 3;
$$;