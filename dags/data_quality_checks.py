"""
Data Quality Checks DAG
=======================
Executa verificações de qualidade de dados no pipeline do Spotify.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator

default_args = {
    'owner': 'spotify_data_quality',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'spotify_data_quality_checks',
    default_args=default_args,
    description='Quality checks para dados do Spotify',
    schedule_interval=timedelta(hours=1),
    catchup=False,
    tags=['spotify', 'quality', 'monitoring']
)

# Quality checks para dados Bronze
bronze_quality_checks = SnowflakeOperator(
    task_id='bronze_quality_checks',
    sql='''
    -- Verificar se há dados novos
    SELECT COUNT(*) as new_records
    FROM SPOTIFY_ANALYTICS.BRONZE.RAW_PLAYS
    WHERE loaded_at >= DATEADD(HOUR, -1, CURRENT_TIMESTAMP());
    ''',
    dag=dag
)

# Quality checks para dados Silver
silver_quality_checks = SnowflakeOperator(
    task_id='silver_quality_checks',
    sql='''
    -- Verificar completude dos dados
    SELECT 
        COUNT(*) as total_records,
        COUNT(DISTINCT user_id) as unique_users,
        COUNT(DISTINCT track_id) as unique_tracks,
        AVG(play_duration_ms) as avg_duration
    FROM SPOTIFY_ANALYTICS.SILVER.PLAYS
    WHERE created_at >= DATEADD(HOUR, -1, CURRENT_TIMESTAMP());
    ''',
    dag=dag
)

# Quality checks para dados Gold
gold_quality_checks = SnowflakeOperator(
    task_id='gold_quality_checks',
    sql='''
    -- Verificar métricas de negócio
    SELECT 
        SUM(total_plays) as total_plays,
        COUNT(DISTINCT user_id) as active_users,
        COUNT(DISTINCT artist_id) as active_artists
    FROM SPOTIFY_ANALYTICS.GOLD.DAILY_PLAYS
    WHERE play_date = CURRENT_DATE();
    ''',
    dag=dag
)

# Alertas para anomalias
anomaly_detection = SnowflakeOperator(
    task_id='anomaly_detection',
    sql='''
    -- Detectar quedas súbitas no volume de dados
    WITH hourly_stats AS (
        SELECT 
            DATE_TRUNC('HOUR', created_at) as hour_bucket,
            COUNT(*) as play_count
        FROM SPOTIFY_ANALYTICS.SILVER.PLAYS
        WHERE created_at >= DATEADD(HOUR, -24, CURRENT_TIMESTAMP())
        GROUP BY 1
    ),
    stats AS (
        SELECT
            AVG(play_count) as avg_plays,
            STDDEV(play_count) as std_plays
        FROM hourly_stats
    )
    SELECT 
        hour_bucket,
        play_count,
        CASE 
            WHEN play_count < (SELECT avg_plays - 2 * std_plays FROM stats) THEN 'LOW'
            WHEN play_count > (SELECT avg_plays + 2 * std_plays FROM stats) THEN 'HIGH'
            ELSE 'NORMAL'
        END as anomaly_status
    FROM hourly_stats
    ORDER BY hour_bucket DESC
    LIMIT 1;
    ''',
    dag=dag
)

# Definir dependências
bronze_quality_checks >> silver_quality_checks
silver_quality_checks >> gold_quality_checks
gold_quality_checks >> anomaly_detection