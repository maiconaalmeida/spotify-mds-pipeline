{{
    config(
        materialized='table',
        unique_key='artist_key',
        tags=['gold', 'artists']
    )
}}

WITH artist_plays AS (
    SELECT
        artist_key,
        COUNT(*) AS total_plays,
        COUNT(DISTINCT user_key) AS unique_listeners,
        COUNT(DISTINCT track_key) AS total_tracks,
        AVG(completion_ratio) AS avg_completion_ratio,
        AVG(danceability) AS avg_danceability,
        AVG(energy) AS avg_energy,
        AVG(valence) AS avg_valence,
        SUM(CASE WHEN is_completed_play = 1 THEN 1 ELSE 0 END) AS completed_plays,
        MIN(event_timestamp) AS first_play_date,
        MAX(event_timestamp) AS last_play_date
    FROM {{ ref('fact_plays') }}
    GROUP BY artist_key
),

artist_regions AS (
    SELECT
        artist_key,
        region_name,
        plays,
        ROUND(plays * 100.0 / SUM(plays) OVER (PARTITION BY artist_key), 2) AS region_percentage
    FROM (
        SELECT
            fp.artist_key,
            dr.region_name,
            COUNT(*) AS plays
        FROM {{ ref('fact_plays') }} fp
        JOIN {{ ref('dim_regions') }} dr ON fp.region_key = dr.region_key
        GROUP BY fp.artist_key, dr.region_name
    )
),

top_region AS (
    SELECT
        artist_key,
        region_name AS top_region,
        region_percentage AS top_region_percentage
    FROM artist_regions
    QUALIFY ROW_NUMBER() OVER (PARTITION BY artist_key ORDER BY plays DESC) = 1
)

SELECT
    ap.artist_key,
    da.artist_name,
    da.genre,
    da.genre_category,
    ap.total_plays,
    ap.unique_listeners,
    ap.total_tracks,
    ap.avg_completion_ratio,
    ap.avg_danceability,
    ap.avg_energy,
    ap.avg_valence,
    ap.completed_plays,
    ap.first_play_date,
    ap.last_play_date,
    tr.top_region,
    tr.top_region_percentage,
    ROUND(ap.unique_listeners * 100.0 / NULLIF(ap.total_plays, 0), 2) AS engagement_ratio,
    DATEDIFF('day', ap.first_play_date, ap.last_play_date) AS days_active,
    CASE 
        WHEN ap.total_plays > 10000 THEN 'Superstar'
        WHEN ap.total_plays > 1000 THEN 'Popular'
        WHEN ap.total_plays > 100 THEN 'Emerging'
        ELSE 'Niche'
    END AS popularity_tier,
    CURRENT_TIMESTAMP() AS calculated_at
FROM artist_plays ap
JOIN {{ ref('dim_artists') }} da ON ap.artist_key = da.artist_key
LEFT JOIN top_region tr ON ap.artist_key = tr.artist_key