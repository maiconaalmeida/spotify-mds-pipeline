#!/usr/bin/env python3
"""
Script para criar conexões do Airflow automaticamente
"""

from airflow.models import Connection
from airflow.utils.db import create_session
import os

def create_connections():
    """Cria conexões do Airflow para o pipeline Spotify"""
    
    connections = [
        {
            'conn_id': 'snowflake_default',
            'conn_type': 'snowflake',
            'host': os.getenv('SNOWFLAKE_ACCOUNT', 'your-account.snowflakecomputing.com'),
            'login': os.getenv('SNOWFLAKE_USER', 'your-username'),
            'password': os.getenv('SNOWFLAKE_PASSWORD', 'your-password'),
            'schema': os.getenv('SNOWFLAKE_DATABASE', 'SPOTIFY_ANALYTICS'),
            'extra': {
                'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
                'database': os.getenv('SNOWFLAKE_DATABASE', 'SPOTIFY_ANALYTICS'),
                'role': os.getenv('SNOWFLAKE_ROLE', 'SYSADMIN')
            }
        },
        {
            'conn_id': 'minio_default',
            'conn_type': 's3',
            'login': os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
            'password': os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
            'extra': {
                'host': 'http://minio:9000'
            }
        },
        {
            'conn_id': 'kafka_default',
            'conn_type': 'kafka',
            'host': 'kafka',
            'port': 9092,
            'extra': {
                'bootstrap_servers': 'kafka:9092'
            }
        }
    ]
    
    with create_session() as session:
        for conn_config in connections:
            conn = Connection(**conn_config)
            session.add(conn)
            print(f"✅ Conexão criada: {conn_config['conn_id']}")
    
    print("🎉 Todas as conexões foram criadas com sucesso!")

if __name__ == "__main__":
    create_connections()