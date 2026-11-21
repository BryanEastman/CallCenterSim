SELECT *
FROM {{ source('bronze', 'calls') }}