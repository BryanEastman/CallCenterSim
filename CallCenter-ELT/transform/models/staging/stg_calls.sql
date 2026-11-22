WITH call_log AS (
    SELECT *
    FROM {{ source('bronze', 'calls') }}
)

SELECT *
    , TO_TIMESTAMP("arrival time"::BIGINT) arrival_datetime_utc
    , TO_TIMESTAMP("handled time"::BIGINT) handled_datetime_utc
    , TO_TIMESTAMP("canceled time"::BIGINT) canceled_datetime_utc
    , TO_TIMESTAMP("completed time"::BIGINT) completed_datetime_utc
FROM call_log