WITH calls AS (
    SELECXT *
    FROM {{ source ('silver', 'stg_calls') }}
)

SELECT *
FROM calls