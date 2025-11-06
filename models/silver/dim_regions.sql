{{
    config(
        materialized='table',
        unique_key='region_key',
        tags=['silver', 'regions']
    )
}}

WITH region_data AS (
    SELECT DISTINCT
        user_region AS region_code
    FROM {{ ref('stg_bronze_plays') }}
    WHERE user_region IS NOT NULL
),

region_mapping AS (
    SELECT 
        region_code,
        CASE region_code
            WHEN 'southeast' THEN 'Sudeste'
            WHEN 'south' THEN 'Sul'
            WHEN 'northeast' THEN 'Nordeste'
            WHEN 'north' THEN 'Norte'
            WHEN 'midwest' THEN 'Centro-Oeste'
            ELSE 'Desconhecida'
        END AS region_name,
        CASE region_code
            WHEN 'southeast' THEN 'SP,RJ,MG,ES'
            WHEN 'south' THEN 'PR,SC,RS'
            WHEN 'northeast' THEN 'BA,PE,CE,MA'
            WHEN 'north' THEN 'AM,PA,RO,AC'
            WHEN 'midwest' THEN 'DF,GO,MT,MS'
            ELSE 'Outros'
        END AS states
    FROM region_data
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['region_code']) }} AS region_key,
    region_code,
    region_name,
    states,
    CURRENT_TIMESTAMP() AS created_at
FROM region_mapping