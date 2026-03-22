-- int_commit_daily: 일별 커밋 집계
-- Table로 구현 (집계 결과 물리적 저장)

CREATE OR REPLACE TABLE int_commit_daily AS
SELECT
    commit_date,
    developer,
    repo_owner,
    repo_name,
    COUNT(*) AS commit_count,
    AVG(message_length) AS avg_message_length
FROM stg_commits
GROUP BY commit_date, developer, repo_owner, repo_name
