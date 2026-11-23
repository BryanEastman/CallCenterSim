WITH call_log AS (
    SELECT "call id"
    , "call state"
    , "call direction"
    , TO_TIMESTAMP("arrival time"::BIGINT) arrival_datetime_cst
    , TO_TIMESTAMP("handled time"::BIGINT) handled_datetime_cst
    , TO_TIMESTAMP("canceled time"::BIGINT) canceled_datetime_cst
    , TO_TIMESTAMP("completed time"::BIGINT) completed_datetime_cst
    FROM {{ source('bronze', 'calls') }}
)

SELECT *
FROM call_log