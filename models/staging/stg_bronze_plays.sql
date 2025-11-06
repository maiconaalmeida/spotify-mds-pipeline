{{
    config(
        materialized='view',
        tags=['staging', 'daily']
    )
}}

WITH raw_plays AS (
    SELECT
        raw_data:event_id::VARCHAR AS event_id,
        raw_data:event_type::VARCHAR AS event_type,
        raw_data:user_id::VARCHAR AS user_id,
        raw_data:user_region::VARCHAR AS user_region,
        raw_data:user_premium::BOOLEAN AS user_premium,
        raw_data:track_id::VARCHAR AS track_id,
        raw_data:track_name::VARCHAR AS track_name,
        raw_data:artist_id::VARCHAR AS artist_id,
        raw_data:artist_name::VARCHAR AS artist_name,
        raw_data:genre::VARCHAR AS genre,
        raw_data:duration_ms::INTEGER AS duration_ms,
        raw_data:play_duration_ms::INTEGER AS play_duration_ms,
        raw_data:device_type::VARCHAR AS device_type,
        raw_data:timestamp::TIMESTAMP_NTZ AS event_timestamp,
        raw_data:explicit::BOOLEAN AS explicit,
        raw_data:audio_features:danceability::FLOAT AS danceability,
        raw_data:audio_features:energy::FLOAT AS energy,
        raw_data:audio_features:valence::FLOAT AS valence,
        raw_data:completed::BOOLEAN AS completed,
        filename,
        loaded_at,
        file_date
    FROM {{ source('bronze', 'raw_plays') }}
    WHERE raw_data:event_type = 'track_play'
)

SELECT
    event_id,
    event_type,
    user_id,
    LOWER(user_region) AS user_region,
    user_premium,
    track_id,
    TRIM(track_name) AS track_name,
    artist_id,
    TRIM(artist_name) AS artist_name,
    LOWER(genre) AS genre,
    duration_ms,
    play_duration_ms,
    device_type,
    event_timestamp,
    explicit,
    danceability,
    energy,
    valence,
    completed,
    filename,
    loaded_at,
    file_date
FROM raw_plays
WHERE event_timestamp IS NOT NULL
  AND user_id IS NOT NULL
  AND track_id IS NOT NULL