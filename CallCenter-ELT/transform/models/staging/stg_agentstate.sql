WITH state_log AS (
    SELECT *
    FROM {{ source('bronze', 'state log') }}
)

SELECT *
    , TO_TIMESTAMP("agent state timestamp"::BIGINT) state_time_utc
FROM state_log