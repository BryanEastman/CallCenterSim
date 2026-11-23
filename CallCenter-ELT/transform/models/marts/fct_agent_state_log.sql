WITH state_log AS (
    SELECT "agent id"
        , "agent state"
        , state_time_cst
    FROM {{ source('silver', 'stg_agentstate')}}
)

SELECT *
FROM state_log