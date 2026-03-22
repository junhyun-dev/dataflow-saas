-- mart_developer_weekly: 주간 개발자 생산성 KPI
-- 회사 CO005 패턴: 여러 intermediate → FULL JOIN → 최종 mart
-- Table로 구현

CREATE OR REPLACE TABLE mart_developer_weekly AS
WITH weekly_commits AS (
    SELECT
        DATE_TRUNC('week', commit_date) AS commit_week,
        developer,
        repo_owner,
        repo_name,
        SUM(commit_count) AS total_commits,
        AVG(avg_message_length) AS avg_message_length
    FROM int_commit_daily
    GROUP BY DATE_TRUNC('week', commit_date), developer, repo_owner, repo_name
),
weekly_prs AS (
    SELECT
        pr_week AS commit_week,
        author AS developer,
        repo_owner,
        repo_name,
        SUM(pr_count) AS total_prs,
        SUM(CASE WHEN pr_status = 'merged' THEN pr_count ELSE 0 END) AS merged_prs,
        AVG(avg_hours_to_merge) AS avg_hours_to_merge
    FROM int_pr_metrics
    GROUP BY pr_week, author, repo_owner, repo_name
)
SELECT
    COALESCE(c.commit_week, p.commit_week) AS week_start,
    COALESCE(c.developer, p.developer) AS developer,
    COALESCE(c.repo_owner, p.repo_owner) AS repo_owner,
    COALESCE(c.repo_name, p.repo_name) AS repo_name,
    COALESCE(c.total_commits, 0) AS total_commits,
    c.avg_message_length,
    COALESCE(p.total_prs, 0) AS total_prs,
    COALESCE(p.merged_prs, 0) AS merged_prs,
    p.avg_hours_to_merge,
    CURRENT_TIMESTAMP AS updated_at
FROM weekly_commits c
FULL OUTER JOIN weekly_prs p
    ON c.commit_week = p.commit_week
    AND c.developer = p.developer
    AND c.repo_owner = p.repo_owner
    AND c.repo_name = p.repo_name
ORDER BY week_start DESC, developer
