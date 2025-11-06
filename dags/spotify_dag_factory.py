"""
DAG Factory para Pipeline Spotify
=================================
Gera DAGs automaticamente para diferentes ambientes.
"""

from airflow import DAG
from datetime import datetime, timedelta

def create_spotify_dag(
    dag_id,
    schedule_interval,
    default_args=None,
    catchup=False,
    tags=None
):
    """
    Factory function para criar DAGs do Spotify.
    """
    if default_args is None:
        default_args = {
            'owner': 'spotify_engineering',
            'depends_on_past': False,
            'start_date': datetime(2024, 1, 1),
            'retries': 2,
            'retry_delay': timedelta(minutes=5)
        }
    
    if tags is None:
        tags = ['spotify', 'data-pipeline']
    
    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        schedule_interval=schedule_interval,
        catchup=catchup,
        tags=tags,
        description=f'Pipeline Spotify - {dag_id}'
    )
    
    # Aqui você pode adicionar tasks programaticamente
    # baseado no dag_id ou outros parâmetros
    
    return dag

# Criar DAGs para diferentes ambientes
development_dag = create_spotify_dag(
    dag_id='spotify_pipeline_dev',
    schedule_interval=timedelta(hours=1),
    tags=['spotify', 'dev']
)

production_dag = create_spotify_dag(
    dag_id='spotify_pipeline_prod',
    schedule_interval=timedelta(minutes=30),
    tags=['spotify', 'prod']
)

backfill_dag = create_spotify_dag(
    dag_id='spotify_pipeline_backfill',
    schedule_interval=None,  # Manual trigger only
    tags=['spotify', 'backfill']
)