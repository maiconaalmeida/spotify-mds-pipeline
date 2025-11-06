{{
    config(
        materialized='incremental',
        unique_key='play_key',
        tags=['silver', 'incremental']
    )
}}

WITH play_events AS (
    SELECT
        sp.event_id,
        sp.event_timestamp,
        sp.user_id,
        sp.track_id,
        sp.artist_id,
        sp.user_region,
        sp.device_type,
        sp.duration_ms,
        sp.play_duration_ms,
        sp.completed,
        sp.danceability,
        sp.energy,
        sp.valence,
        sp.explicit,
        sp.user_premium
    FROM {{ ref('stg_bronze_plays') }} sp
    {% if is_incremental() %}
    WHERE sp.event_timestamp > (SELECT MAX(event_timestamp) FROM {{ this }})
    {% endif %}
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['event_id']) }} AS play_key,
    du.user_key,
    dt.track_key,
    da.artist_key,
    dd.device_key,
    dr.region_key,
    {{ dbt_utils.generate_surrogate_key(["DATE(pe.event_timestamp)"]) }} AS date_key,
    pe.event_id,
    pe.event_timestamp,
    pe.duration_ms,
    pe.play_duration_ms,
    pe.completed,
    pe.danceability,
    pe.energy,
    pe.valence,
    pe.explicit,
    pe.user_premium,
    CASE 
        WHEN pe.play_duration_ms >= pe.duration_ms * 0.9 THEN 1 
        ELSE 0 
    END AS is_completed_play,
    CASE 
        WHEN pe.play_duration_ms < 30000 THEN 'Skip'
        WHEN pe.play_duration_ms < pe.duration_ms * 0.5 THEN 'Partial'
        ELSE 'Full'
    END AS play_completion_type,
    pe.play_duration_ms / pe.duration_ms AS completion_ratio,
    EXTRACT(HOUR FROM pe.event_timestamp) AS hour_of_day,
    CASE 
        WHEN EXTRACT(HOUR FROM pe.event_timestamp) BETWEEN 6 AND 11 THEN 'Morning'
        WHEN EXTRACT(HOUR FROM pe.event_timestamp) BETWEEN 12 AND 17 THEN 'Afternoon'
        WHEN EXTRACT(HOUR FROM pe.event_timestamp) BETWEEN 18 AND 23 THEN 'Evening'
        ELSE 'Night'
    END AS time_of_day,
    CURRENT_TIMESTAMP() AS created_at
FROM play_events pe
LEFT JOIN {{ ref('dim_users') }} du ON pe.user_id = du.user_id
LEFT JOIN {{ ref('dim_tracks') }} dt ON pe.track_id = dt.track_id
LEFT JOIN {{ ref('dim_artists') }} da ON pe.artist_id = da.artist_id
LEFT JOIN {{ ref('dim_devices') }} dd ON pe.device_type = dd.device_type
LEFT JOIN {{ ref('dim_regions') }} dr ON pe.user_region = dr.region_code