{{
    config(
        materialized='table',
        unique_key='track_key',
        tags=['silver', 'tracks']
    )
}}

WITH track_data AS (
    SELECT
        track_id,
        track_name,
        artist_id,
        duration_ms,
        explicit,
        danceability,
        energy,
        valence
    FROM {{ ref('stg_bronze_plays') }}
    WHERE track_id IS NOT NULL
    QUALIFY ROW_NUMBER() OVER (PARTITION BY track_id ORDER BY event_timestamp DESC) = 1
),

enriched_tracks AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['track_id']) }} AS track_key,
        track_id,
        track_name,
        artist_id,
        duration_ms,
        explicit,
        danceability,
        energy,
        valence,
        CASE 
            WHEN duration_ms < 180000 THEN 'Curta (<3min)'
            WHEN duration_ms BETWEEN 180000 AND 300000 THEN 'Média (3-5min)'
            ELSE 'Longa (>5min)'
        END AS duration_category,
        CASE 
            WHEN danceability > 0.7 THEN 'Alta Dançabilidade'
            WHEN danceability > 0.4 THEN 'Média Dançabilidade'
            ELSE 'Baixa Dançabilidade'
        END AS danceability_category,
        CASE 
            WHEN energy > 0.7 THEN 'Alta Energia'
            WHEN energy > 0.4 THEN 'Média Energia'
            ELSE 'Baixa Energia'
        END AS energy_category,
        CURRENT_TIMESTAMP() AS created_at
    FROM track_data
)

SELECT * FROM enriched_tracks