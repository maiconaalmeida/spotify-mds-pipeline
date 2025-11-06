{{
    config(
        materialized='table',
        tags=['marts', 'business']
    )
}}

WITH daily_kpis AS (
    SELECT
        date_key,
        total_plays,
        unique_users,
        unique_tracks,
        unique_artists,
        completion_rate_pct,
        premium_rate_pct,
        mobile_plays,
        desktop_plays,
        speaker_plays,
        morning_plays,
        afternoon_plays,
        evening_plays,
        night_plays
    FROM {{ ref('fct_daily_plays') }}
),

rolling_metrics AS (
    SELECT
        date_key,
        total_plays,
        unique_users,
        AVG(total_plays) OVER (ORDER BY date_key ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS avg_plays_7d,
        AVG(unique_users) OVER (ORDER BY date_key ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS avg_users_7d,
        LAG(total_plays, 7) OVER (ORDER BY date_key) AS plays_7d_ago,
        LAG(unique_users, 7) OVER (ORDER BY date_key) AS users_7d_ago
    FROM daily_kpis
)

SELECT
    dk.date_key,
    dt.full_date,
    dk.total_plays,
    dk.unique_users,
    dk.unique_tracks,
    dk.unique_artists,
    dk.completion_rate_pct,
    dk.premium_rate_pct,
    rm.avg_plays_7d,
    rm.avg_users_7d,
    dk.mobile_plays,
    dk.desktop_plays,
    dk.speaker_plays,
    dk.morning_plays,
    dk.afternoon_plays,
    dk.evening_plays,
    dk.night_plays,
    ROUND((dk.total_plays - rm.plays_7d_ago) * 100.0 / NULLIF(rm.plays_7d_ago, 0), 2) AS plays_growth_7d_pct,
    ROUND((dk.unique_users - rm.users_7d_ago) * 100.0 / NULLIF(rm.users_7d_ago, 0), 2) AS users_growth_7d_pct,
    ROUND(dk.mobile_plays * 100.0 / NULLIF(dk.total_plays, 0), 2) AS mobile_ratio_pct,
    ROUND(dk.premium_plays * 100.0 / NULLIF(dk.total_plays, 0), 2) AS premium_ratio_pct,
    CURRENT_TIMESTAMP() AS calculated_at
FROM daily_kpis dk
JOIN rolling_metrics rm ON dk.date_key = rm.date_key
JOIN {{ ref('dim_time') }} dt ON dk.date_key = dt.time_key