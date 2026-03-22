-- stg_commits: raw 정제 + 날짜 파생 컬럼
-- View로 구현 (원본 데이터 복사 불필요)

CREATE OR REPLACE VIEW stg_commits AS
SELECT
    sha,
    message,
    author_name,
    author_email,
    author_date,
    committer_date,
    repo_owner,
    repo_name,
    -- 파생 컬럼
    DATE_TRUNC('day', author_date) AS commit_date,
    DATE_TRUNC('week', author_date) AS commit_week,
    LENGTH(message) AS message_length
FROM raw_commits
