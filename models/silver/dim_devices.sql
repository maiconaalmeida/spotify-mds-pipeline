{{
    config(
        materialized='table',
        unique_key='device_key',
        tags=['silver', 'devices']
    )
}}

WITH device_data AS (
    SELECT DISTINCT
        device_type
    FROM {{ ref('stg_bronze_plays') }}
    WHERE device_type IS NOT NULL
),

enriched_devices AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['device_type']) }} AS device_key,
        device_type,
        CASE 
            WHEN device_type IN ('mobile', 'tablet') THEN 'Mobile'
            WHEN device_type = 'desktop' THEN 'Desktop'
            WHEN device_type = 'smart_speaker' THEN 'Smart Speaker'
            WHEN device_type = 'car_system' THEN 'Car System'
            ELSE 'Other'
        END AS device_category,
        CASE 
            WHEN device_type IN ('mobile', 'tablet') THEN 'Portable'
            ELSE 'Fixed'
        END AS device_mobility,
        CURRENT_TIMESTAMP() AS created_at
    FROM device_data
)

SELECT * FROM enriched_devices