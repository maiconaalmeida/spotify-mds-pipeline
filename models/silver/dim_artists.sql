{{
    config(
        materialized='table',
        unique_key='artist_key',
        tags=['silver', 'artists']
    )
}}

WITH artist_data AS (
    SELECT DISTINCT
        artist_id,
        artist_name,
        genre
    FROM {{ ref('stg_bronze_plays') }}
    WHERE artist_id IS NOT NULL
),

enriched_artists AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['artist_id']) }} AS artist_key,
        artist_id,
        artist_name,
        genre,
        CASE 
            WHEN genre IN ('sertanejo', 'forró', 'piseiro') THEN 'Sertanejo'
            WHEN genre IN ('funk', 'funk carioca') THEN 'Funk'
            WHEN genre IN ('samba', 'pagode') THEN 'Samba'
            WHEN genre IN ('mpb', 'bossa nova') THEN 'MPB'
            WHEN genre IN ('rock', 'rock nacional') THEN 'Rock'
            WHEN genre IN ('pop', 'pop nacional') THEN 'Pop'
            WHEN genre IN ('eletrônica', 'house', 'techno') THEN 'Eletrônica'
            WHEN genre IN ('rap', 'hip hop') THEN 'Rap/Hip Hop'
            ELSE 'Outros'
        END AS genre_category,
        LENGTH(artist_name) AS name_length,
        CURRENT_TIMESTAMP() AS created_at,
        CURRENT_TIMESTAMP() AS updated_at
    FROM artist_data
)

SELECT * FROM enriched_artists