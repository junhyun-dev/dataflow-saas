-- int_pr_metrics: PR 메트릭 주간 집계
-- Table로 구현

CREATE OR REPLACE TABLE int_pr_metrics AS
SELECT
    pr_week,
    author,
    pr_status,
    repo_owner,
    repo_name,
    COUNT(*) AS pr_count,
    AVG(hours_to_merge) AS avg_hours_to_merge
FROM stg_pull_requests
GROUP BY pr_week, author, pr_status, repo_owner, repo_name
