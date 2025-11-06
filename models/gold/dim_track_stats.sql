{{
    config(
        materialized='table',
        unique_key='track_key',
        tags=['gold', 'tracks']
    )
}}

WITH track_plays AS (
    SELECT
        track_key,
        COUNT(*) AS total_plays,
        COUNT(DISTINCT user_key) AS unique_listeners,
        AVG(completion_ratio) AS avg_completion_ratio,
        SUM(CASE WHEN is_completed_play = 1 THEN 1 ELSE 0 END) AS completed_plays,
        MIN(event_timestamp) AS first_play_date,
        MAX(event_timestamp) AS last_play_date,
        AVG(danceability) AS avg_danceability,
        AVG(energy) AS avg_energy,
        AVG(valence) AS avg_valence
    FROM {{ ref('fact_plays') }}
    GROUP BY track_key
)

SELECT
    tp.track_key,
    dt.track_name,
    da.artist_name,
    dt.duration_ms,
    dt.duration_category,
    dt.explicit,
    tp.total_plays,
    tp.unique_listeners,
    tp.avg_completion_ratio,
    tp.completed_plays,
    tp.first_play_date,
    tp.last_play_date,
    tp.avg_danceability,
    tp.avg_energy,
    tp.avg_valence,
    ROUND(tp.completed_plays * 100.0 / NULLIF(tp.total_plays, 0), 2) AS completion_rate,
    ROUND(tp.unique_listeners * 100.0 / NULLIF(tp.total_plays, 0), 2) AS listener_retention_rate,
    DATEDIFF('day', tp.first_play_date, tp.last_play_date) AS days_in_rotation,
    CASE 
        WHEN tp.total_plays > 5000 THEN 'Viral'
        WHEN tp.total_plays > 1000 THEN 'Hit'
        WHEN tp.total_plays > 100 THEN 'Popular'
        ELSE 'Regular'
    END AS popularity_tier,
    CURRENT_TIMESTAMP() AS calculated_at
FROM track_plays tp
JOIN {{ ref('dim_tracks') }} dt ON tp.track_key = dt.track_key
JOIN {{ ref('dim_artists') }} da ON dt.artist_id = da.artist_id