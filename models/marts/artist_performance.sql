{{
    config(
        materialized='table',
        tags=['marts', 'analytics']
    )
}}

SELECT
    das.artist_key,
    das.artist_name,
    das.genre,
    das.genre_category,
    das.total_plays,
    das.unique_listeners,
    das.total_tracks,
    das.engagement_ratio,
    das.popularity_tier,
    das.top_region,
    das.top_region_percentage,
    RANK() OVER (ORDER BY das.total_plays DESC) AS rank_total_plays,
    RANK() OVER (ORDER BY das.unique_listeners DESC) AS rank_unique_listeners,
    RANK() OVER (PARTITION BY das.genre_category ORDER BY das.total_plays DESC) AS rank_in_genre,
    CASE 
        WHEN das.popularity_tier = 'Superstar' AND das.engagement_ratio > 50 THEN 'Superstar High Engagement'
        WHEN das.popularity_tier = 'Superstar' THEN 'Superstar Regular'
        WHEN das.popularity_tier = 'Popular' AND das.engagement_ratio > 60 THEN 'Popular Rising'
        ELSE das.popularity_tier
    END AS artist_segment,
    CURRENT_TIMESTAMP() AS analyzed_at
FROM {{ ref('dim_artist_stats') }} das
WHERE das.total_plays > 0