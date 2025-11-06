{{
    config(
        materialized='table',
        tags=['gold', 'daily']
    )
}}

WITH daily_plays AS (
    SELECT
        date_key,
        COUNT(*) AS total_plays,
        COUNT(DISTINCT user_key) AS unique_users,
        COUNT(DISTINCT track_key) AS unique_tracks,
        COUNT(DISTINCT artist_key) AS unique_artists,
        SUM(CASE WHEN is_completed_play = 1 THEN 1 ELSE 0 END) AS completed_plays,
        AVG(completion_ratio) AS avg_completion_ratio,
        AVG(danceability) AS avg_danceability,
        AVG(energy) AS avg_energy,
        AVG(valence) AS avg_valence,
        SUM(CASE WHEN user_premium = TRUE THEN 1 ELSE 0 END) AS premium_plays,
        SUM(CASE WHEN explicit = TRUE THEN 1 ELSE 0 END) AS explicit_plays
    FROM {{ ref('fact_plays') }}
    GROUP BY date_key
),

device_breakdown AS (
    SELECT
        date_key,
        device_category,
        COUNT(*) AS plays
    FROM {{ ref('fact_plays') }} fp
    JOIN {{ ref('dim_devices') }} dd ON fp.device_key = dd.device_key
    GROUP BY date_key, device_category
),

time_breakdown AS (
    SELECT
        date_key,
        time_of_day,
        COUNT(*) AS plays
    FROM {{ ref('fact_plays') }}
    GROUP BY date_key, time_of_day
)

SELECT
    dp.date_key,
    dp.total_plays,
    dp.unique_users,
    dp.unique_tracks,
    dp.unique_artists,
    dp.completed_plays,
    dp.avg_completion_ratio,
    dp.avg_danceability,
    dp.avg_energy,
    dp.avg_valence,
    dp.premium_plays,
    dp.explicit_plays,
    ROUND(dp.completed_plays * 100.0 / NULLIF(dp.total_plays, 0), 2) AS completion_rate_pct,
    ROUND(dp.premium_plays * 100.0 / NULLIF(dp.total_plays, 0), 2) AS premium_rate_pct,
    db_mobile.plays AS mobile_plays,
    db_desktop.plays AS desktop_plays,
    db_speaker.plays AS speaker_plays,
    tb_morning.plays AS morning_plays,
    tb_afternoon.plays AS afternoon_plays,
    tb_evening.plays AS evening_plays,
    tb_night.plays AS night_plays,
    CURRENT_TIMESTAMP() AS created_at
FROM daily_plays dp
LEFT JOIN device_breakdown db_mobile ON dp.date_key = db_mobile.date_key AND db_mobile.device_category = 'Mobile'
LEFT JOIN device_breakdown db_desktop ON dp.date_key = db_desktop.date_key AND db_desktop.device_category = 'Desktop'
LEFT JOIN device_breakdown db_speaker ON dp.date_key = db_speaker.date_key AND db_speaker.device_category = 'Smart Speaker'
LEFT JOIN time_breakdown tb_morning ON dp.date_key = tb_morning.date_key AND tb_morning.time_of_day = 'Morning'
LEFT JOIN time_breakdown tb_afternoon ON dp.date_key = tb_afternoon.date_key AND tb_afternoon.time_of_day = 'Afternoon'
LEFT JOIN time_breakdown tb_evening ON dp.date_key = tb_evening.date_key AND tb_evening.time_of_day = 'Evening'
LEFT JOIN time_breakdown tb_night ON dp.date_key = tb_night.date_key AND tb_night.time_of_day = 'Night'