-- Supabase schema for the math practice system.
-- Run this file in the Supabase SQL Editor.
-- WARNING: this script performs a full reset of app tables/functions in public schema.

BEGIN;

-- Full reset: drop RPCs and tables first, then recreate everything.
DROP FUNCTION IF EXISTS get_random_problems(TEXT, TEXT[], INTEGER);
DROP FUNCTION IF EXISTS get_user_statistics(BIGINT);
DROP FUNCTION IF EXISTS get_similar_problems(TEXT, INTEGER, BIGINT);

DROP TABLE IF EXISTS wrong_problems;
DROP TABLE IF EXISTS user_answers;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS problems;

-- problems table
-- The subject/grade/project scope is stored inside the tags column
-- using tags such as "科目:数学", "年级:小二下", "项目:一位数和两位数加减法".
CREATE TABLE problems (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    question TEXT NOT NULL,
    num1 INTEGER NOT NULL,
    num2 INTEGER NOT NULL,
    answer INTEGER NOT NULL,
    type TEXT NOT NULL,
    tags TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- users table
CREATE TABLE users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    practice_settings JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- user_answers table
CREATE TABLE user_answers (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    problem_id BIGINT NOT NULL REFERENCES problems(id),
    user_answer INTEGER NOT NULL,
    is_correct BOOLEAN NOT NULL,
    answered_at TIMESTAMPTZ DEFAULT NOW()
);

-- wrong_problems table
CREATE TABLE wrong_problems (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    problem_id BIGINT NOT NULL REFERENCES problems(id),
    tags TEXT NOT NULL,
    wrong_count INTEGER DEFAULT 1,
    correct_streak INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, problem_id)
);

-- indexes
CREATE INDEX idx_user_answers_user_id ON user_answers(user_id);
CREATE INDEX idx_user_answers_problem_id ON user_answers(problem_id);
CREATE INDEX idx_problems_type ON problems(type);
CREATE INDEX idx_wrong_problems_user_id ON wrong_problems(user_id);

-- RPC: get random problems
CREATE OR REPLACE FUNCTION get_random_problems(
    p_type TEXT DEFAULT NULL,
    p_tags TEXT[] DEFAULT NULL,
    p_count INTEGER DEFAULT 10
)
RETURNS SETOF problems
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM problems p
    WHERE (p_type IS NULL OR p.type = p_type)
      AND (
          p_tags IS NULL OR NOT EXISTS (
              SELECT 1
              FROM unnest(p_tags) AS t(tag)
              WHERE p.tags NOT LIKE '%' || t.tag || '%'
          )
      )
    ORDER BY RANDOM()
    LIMIT p_count;
END;
$$;

-- RPC: get user statistics
CREATE OR REPLACE FUNCTION get_user_statistics(p_user_id BIGINT)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_answers', COUNT(*),
        'correct_count', COALESCE(SUM(CASE WHEN is_correct THEN 1 ELSE 0 END), 0),
        'wrong_count', COALESCE(SUM(CASE WHEN NOT is_correct THEN 1 ELSE 0 END), 0)
    ) INTO result
    FROM user_answers
    WHERE user_id = p_user_id;

    RETURN result;
END;
$$;

-- RPC: get similar problems that match at least two tags
CREATE OR REPLACE FUNCTION get_similar_problems(
    p_tags TEXT,
    p_count INTEGER DEFAULT 10,
    p_exclude_id BIGINT DEFAULT NULL
)
RETURNS SETOF problems
LANGUAGE plpgsql
AS $$
DECLARE
    tags_arr TEXT[];
    i INTEGER;
    j INTEGER;
    conditions TEXT[] := '{}';
BEGIN
    tags_arr := string_to_array(p_tags, ',');

    FOR i IN 1..array_length(tags_arr, 1) LOOP
        FOR j IN (i + 1)..array_length(tags_arr, 1) LOOP
            conditions := array_append(
                conditions,
                format(
                    '(tags LIKE ''%%%s%%'' AND tags LIKE ''%%%s%%'')',
                    trim(tags_arr[i]),
                    trim(tags_arr[j])
                )
            );
        END LOOP;
    END LOOP;

    IF array_length(conditions, 1) IS NULL OR array_length(conditions, 1) = 0 THEN
        RETURN;
    END IF;

    RETURN QUERY EXECUTE format(
        'SELECT * FROM problems WHERE (%s) AND ($1 IS NULL OR id != $1) ORDER BY RANDOM() LIMIT $2',
        array_to_string(conditions, ' OR ')
    ) USING p_exclude_id, p_count;
END;
$$;

-- Optional: enable Row Level Security as needed.
-- ALTER TABLE problems ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_answers ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE wrong_problems ENABLE ROW LEVEL SECURITY;

-- If you use the anon key, add policies that allow your app to read and write.
-- CREATE POLICY "Allow anonymous read" ON problems FOR SELECT USING (true);
-- CREATE POLICY "Allow anonymous all" ON users FOR ALL USING (true);
-- CREATE POLICY "Allow anonymous all" ON user_answers FOR ALL USING (true);
-- CREATE POLICY "Allow anonymous all" ON wrong_problems FOR ALL USING (true);

COMMIT;
