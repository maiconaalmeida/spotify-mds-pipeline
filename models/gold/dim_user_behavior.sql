{{
    config(
        materialized='table',
        unique_key='user_key',
        tags=['gold', 'users']
    )
}}

WITH user_behavior AS (
    SELECT
        user_key,
        COUNT(*) AS total_plays,
        COUNT(DISTINCT track_key) AS unique_tracks_played,
        COUNT(DISTINCT artist_key) AS unique_artists_played,
        AVG(completion_ratio) AS avg_completion_ratio,
        AVG(danceability) AS avg_danceability_preference,
        AVG(energy) AS avg_energy_preference,
        AVG(valence) AS avg_valence_preference,
        MIN(event_timestamp) AS first_play_date,
        MAX(event_timestamp) AS last_play_date,
        COUNT(DISTINCT device_key) AS devices_used,
        SUM(CASE WHEN time_of_day = 'Morning' THEN 1 ELSE 0 END) AS morning_plays,
        SUM(CASE WHEN time_of_day = 'Afternoon' THEN 1 ELSE 0 END) AS afternoon_plays,
        SUM(CASE WHEN time_of_day = 'Evening' THEN 1 ELSE 0 END) AS evening_plays,
        SUM(CASE WHEN time_of_day = 'Night' THEN 1 ELSE 0 END) AS night_plays
    FROM {{ ref('fact_plays') }}
    GROUP BY user_key
),

user_preferences AS (
    SELECT
        user_key,
        genre,
        COUNT(*) AS genre_plays
    FROM {{ ref('fact_plays') }} fp
    JOIN {{ ref('dim_artists') }} da ON fp.artist_key = da.artist_key
    GROUP BY user_key, genre
    QUALIFY ROW_NUMBER() OVER (PARTITION BY user_key ORDER BY genre_plays DESC) = 1
)

SELECT
    ub.user_key,
    du.user_id,
    du.user_region,
    du.user_premium,
    du.preferred_device,
    du.user_segment,
    ub.total_plays,
    ub.unique_tracks_played,
    ub.unique_artists_played,
    ub.avg_completion_ratio,
    ub.avg_danceability_preference,
    ub.avg_energy_preference,
    ub.avg_valence_preference,
    ub.first_play_date,
    ub.last_play_date,
    ub.devices_used,
    ub.morning_plays,
    ub.afternoon_plays,
    ub.evening_plays,
    ub.night_plays,
    up.genre AS favorite_genre,
    DATEDIFF('day', ub.first_play_date, ub.last_play_date) AS user_lifetime_days,
    ROUND(ub.unique_tracks_played * 100.0 / NULLIF(ub.total_plays, 0), 2) AS exploration_rate,
    CASE 
        WHEN ub.avg_completion_ratio > 0.8 THEN 'Completer'
        WHEN ub.avg_completion_ratio > 0.5 THEN 'Partial Listener'
        ELSE 'Skipper'
    END AS listening_behavior,
    CASE 
        WHEN ub.avg_energy_preference > 0.7 THEN 'High Energy'
        WHEN ub.avg_energy_preference > 0.4 THEN 'Medium Energy'
        ELSE 'Low Energy'
    END AS energy_preference,
    CURRENT_TIMESTAMP() AS calculated_at
FROM user_behavior ub
JOIN {{ ref('dim_users') }} du ON ub.user_key = du.user_key
LEFT JOIN user_preferences up ON ub.user_key = up.user_key