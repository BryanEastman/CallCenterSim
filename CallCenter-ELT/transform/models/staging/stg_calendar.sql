WITH dates AS (
    SELECT day
    FROM generate_series(DATE '2026-01-01', DATE '2027-01-01', INTERVAL '1 day') AS t(day)
)
SELECT DATE(d.day) date
	, WEEK (d.day) week_number
    , MONTH(d.day) month_number
    , QUARTER(d.day) quarter_number
    , YEAR(d.day) year_number
    , DAYOFWEEK(d.day) weekday_number
    , DAYNAME(d.day) weekday_name
FROM dates d