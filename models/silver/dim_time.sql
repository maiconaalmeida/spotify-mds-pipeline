{{
    config(
        materialized='table',
        unique_key='time_key',
        tags=['silver', 'time']
    )
}}

WITH date_spine AS (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="CAST('2024-01-01' AS DATE)",
        end_date="CAST('2025-12-31' AS DATE)"
    ) }}
),

enriched_dates AS (
    SELECT
        date_day AS time_key,
        date_day AS full_date,
        EXTRACT(YEAR FROM date_day) AS year,
        EXTRACT(MONTH FROM date_day) AS month,
        EXTRACT(DAY FROM date_day) AS day,
        EXTRACT(QUARTER FROM date_day) AS quarter,
        EXTRACT(DAYOFWEEK FROM date_day) AS day_of_week,
        EXTRACT(DAYOFYEAR FROM date_day) AS day_of_year,
        EXTRACT(WEEK FROM date_day) AS week_of_year,
        DATE_PART('day', DATE_TRUNC('month', date_day) - INTERVAL '1 month') AS days_in_previous_month,
        CASE 
            WHEN EXTRACT(DAYOFWEEK FROM date_day) IN (1, 7) THEN 'Weekend'
            ELSE 'Weekday'
        END AS day_type,
        CASE 
            WHEN EXTRACT(MONTH FROM date_day) IN (12, 1, 2) THEN 'Summer'
            WHEN EXTRACT(MONTH FROM date_day) IN (3, 4, 5) THEN 'Autumn'
            WHEN EXTRACT(MONTH FROM date_day) IN (6, 7, 8) THEN 'Winter'
            ELSE 'Spring'
        END AS season,
        CURRENT_TIMESTAMP() AS created_at
    FROM date_spine
)

SELECT * FROM enriched_dates