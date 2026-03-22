-- stg_pull_requests: raw 정제 + PR 상태/시간 파생
-- View로 구현

CREATE OR REPLACE VIEW stg_pull_requests AS
SELECT
    number,
    title,
    state,
    author,
    head_ref,
    base_ref,
    created_at,
    updated_at,
    closed_at,
    merged_at,
    repo_owner,
    repo_name,
    -- 파생: 실제 상태 (GitHub state는 open/closed뿐)
    CASE
        WHEN merged_at IS NOT NULL THEN 'merged'
        WHEN state = 'closed' THEN 'closed'
        ELSE 'open'
    END AS pr_status,
    -- 파생: merge까지 걸린 시간 (hours)
    CASE
        WHEN merged_at IS NOT NULL
        THEN DATE_DIFF('hour', created_at, merged_at)
    END AS hours_to_merge,
    -- 파생: 주 단위 그룹핑용
    DATE_TRUNC('week', created_at) AS pr_week
FROM raw_pull_requests
