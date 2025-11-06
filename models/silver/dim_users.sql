{{
    config(
        materialized='table',
        unique_key='user_key',
        tags=['silver', 'users']
    )
}}

WITH user_events AS (
    SELECT
        user_id,
        user_region,
        user_premium,
        MIN(event_timestamp) AS first_play_date,
        MAX(event_timestamp) AS last_play_date,
        COUNT(*) AS total_plays
    FROM {{ ref('stg_bronze_plays') }}
    WHERE user_id IS NOT NULL
    GROUP BY 1, 2, 3
),

user_devices AS (
    SELECT
        user_id,
        device_type,
        COUNT(*) AS device_plays
    FROM {{ ref('stg_bronze_plays') }}
    GROUP BY 1, 2
    QUALIFY ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY device_plays DESC) = 1
),

enriched_users AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['user_id']) }} AS user_key,
        ue.user_id,
        ue.user_region,
        ue.user_premium,
        ud.device_type AS preferred_device,
        ue.first_play_date,
        ue.last_play_date,
        ue.total_plays,
        DATEDIFF('day', ue.first_play_date, CURRENT_DATE()) AS days_since_first_play,
        CASE 
            WHEN ue.total_plays > 1000 THEN 'Power User'
            WHEN ue.total_plays > 100 THEN 'Active User'
            ELSE 'Casual User'
        END AS user_segment,
        CURRENT_TIMESTAMP() AS created_at,
        CURRENT_TIMESTAMP() AS updated_at
    FROM user_events ue
    LEFT JOIN user_devices ud ON ue.user_id = ud.user_id
)

SELECT * FROM enriched_users