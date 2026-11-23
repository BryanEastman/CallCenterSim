WITH calls AS (
    SELECT *
    FROM {{ source ('silver', 'stg_calls') }}
)

SELECT *
FROM calls