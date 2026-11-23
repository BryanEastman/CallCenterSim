WITH state_log AS (
    SELECT "agent id"
        , "agent state"
        , TO_TIMESTAMP("agent state timestamp"::BIGINT) state_time_cst
    FROM {{ source('bronze', 'state log') }}
)

SELECT *
FROM state_log