"""
Spotify Data Pipeline DAG
=========================
Orquestra o pipeline completo de dados do Spotify:
1. Carga de dados do MinIO para Snowflake (Bronze)
2. Transformações com DBT (Silver → Gold)
3. Quality checks e monitoramento

Autor: Maicon Almeida
Data: 2024
"""

from datetime import datetime, timedelta
import logging
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.exceptions import AirflowException
import requests
import json

# Configuração de logging
logger = logging.getLogger('airflow.task')

# Argumentos padrão do DAG
default_args = {
    'owner': 'spotify_engineering',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
    'snowflake_conn_id': 'snowflake_default'
}

# Definir o DAG
dag = DAG(
    'spotify_data_pipeline',
    default_args=default_args,
    description='Pipeline completo de dados do Spotify - Bronze to Gold',
    schedule_interval=timedelta(minutes=30),  # Executar a cada 30 minutos
    catchup=False,
    tags=['spotify', 'music', 'analytics', 'mds'],
    max_active_runs=1
)

def check_minio_data_availability(**context):
    """
    Verifica se há novos dados disponíveis no MinIO.
    """
    import boto3
    from botocore.client import Config
    
    try:
        # Configurar cliente MinIO
        minio_client = boto3.client(
            's3',
            endpoint_url='http://minio:9000',
            aws_access_key_id='minioadmin',
            aws_secret_access_key='minioadmin',
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )
        
        # Listar objetos no bucket
        response = minio_client.list_objects_v2(
            Bucket='spotify-data',
            Prefix='raw/',
            MaxKeys=10
        )
        
        file_count = response.get('KeyCount', 0)
        context['ti'].xcom_push(key='minio_file_count', value=file_count)
        
        if file_count > 0:
            logger.info(f"Encontrados {file_count} arquivos no MinIO")
            return True
        else:
            logger.warning("Nenhum arquivo encontrado no MinIO")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao verificar MinIO: {e}")
        raise AirflowException(f"Falha na verificação do MinIO: {e}")

def check_kafka_health(**context):
    """
    Verifica a saúde do cluster Kafka.
    """
    try:
        from kafka import KafkaAdminClient
        from kafka.errors import KafkaError
        
        # Tentar conectar ao Kafka
        admin_client = KafkaAdminClient(
            bootstrap_servers=['kafka:9092'],
            client_id='airflow_health_check'
        )
        
        # Listar tópicos
        topics = admin_client.list_topics()
        has_spotify_topic = 'spotify-plays' in topics
        
        context['ti'].xcom_push(key='kafka_healthy', value=True)
        context['ti'].xcom_push(key='spotify_topic_exists', value=has_spotify_topic)
        
        logger.info(f"Kafka saudável. Tópicos disponíveis: {len(topics)}")
        logger.info(f"Tópico spotify-plays existe: {has_spotify_topic}")
        
        admin_client.close()
        return True
        
    except Exception as e:
        logger.error(f"Erro na verificação do Kafka: {e}")
        context['ti'].xcom_push(key='kafka_healthy', value=False)
        raise AirflowException(f"Kafka não está saudável: {e}")

def validate_snowflake_connection(**context):
    """
    Valida a conexão com o Snowflake e verifica tabelas.
    """
    try:
        hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
        conn = hook.get_conn()
        cursor = conn.cursor()
        
        # Verificar se o database existe
        cursor.execute("SHOW DATABASES LIKE 'SPOTIFY_ANALYTICS'")
        db_exists = cursor.fetchone() is not None
        
        if db_exists:
            # Verificar tabelas na camada Bronze
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM SPOTIFY_ANALYTICS.INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = 'BRONZE'
            """)
            bronze_tables = [row[0] for row in cursor.fetchall()]
        else:
            bronze_tables = []
        
        context['ti'].xcom_push(key='snowflake_connected', value=True)
        context['ti'].xcom_push(key='database_exists', value=db_exists)
        context['ti'].xcom_push(key='bronze_tables', value=bronze_tables)
        
        logger.info(f"Conexão Snowflake validada. Database existe: {db_exists}")
        logger.info(f"Tabelas Bronze: {bronze_tables}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Erro na validação do Snowflake: {e}")
        raise AirflowException(f"Falha na conexão com Snowflake: {e}")

def send_slack_notification(**context):
    """
    Envia notificação do Slack sobre o status do pipeline.
    """
    slack_webhook = context['dag_run'].conf.get('slack_webhook') or \
                   'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    
    task_instance = context['ti']
    dag_id = context['dag'].dag_id
    execution_date = context['execution_date']
    
    message = {
        "text": f"🎵 *Pipeline Spotify - Execução Completa*",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎵 Spotify Data Pipeline Status"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*DAG:* {dag_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Execução:* {execution_date}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:* ✅ Sucesso"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Tempo:* {task_instance.duration:.1f}s"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            slack_webhook,
            data=json.dumps(message),
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        logger.info("Notificação Slack enviada com sucesso")
    except Exception as e:
        logger.warning(f"Falha ao enviar notificação Slack: {e}")

# Operadores do DAG

# Início do pipeline
start_pipeline = DummyOperator(
    task_id='start_pipeline',
    dag=dag
)

# Verificações de saúde
check_kafka_health_task = PythonOperator(
    task_id='check_kafka_health',
    python_callable=check_kafka_health,
    dag=dag
)

check_minio_data_task = PythonOperator(
    task_id='check_minio_data_availability',
    python_callable=check_minio_data_availability,
    dag=dag
)

validate_snowflake_task = PythonOperator(
    task_id='validate_snowflake_connection',
    python_callable=validate_snowflake_connection,
    dag=dag
)

# Carga de dados Bronze
create_bronze_tables = SnowflakeOperator(
    task_id='create_bronze_tables',
    sql='''
    CREATE SCHEMA IF NOT EXISTS SPOTIFY_ANALYTICS.BRONZE;
    
    CREATE TABLE IF NOT EXISTS SPOTIFY_ANALYTICS.BRONZE.RAW_PLAYS (
        raw_data VARIANT,
        filename VARCHAR,
        loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
        file_date DATE
    );
    ''',
    dag=dag
)

load_minio_to_bronze = SnowflakeOperator(
    task_id='load_minio_to_bronze',
    sql='''
    COPY INTO SPOTIFY_ANALYTICS.BRONZE.RAW_PLAYS (raw_data, filename, file_date)
    FROM (
        SELECT 
            $1::VARIANT as raw_data,
            metadata$filename as filename,
            CURRENT_DATE() as file_date
        FROM @SPOTIFY_ANALYTICS.PUBLIC.MINIO_STAGE/raw/
    )
    FILE_FORMAT = (TYPE = 'JSON')
    PATTERN = '.*\\.json'
    ON_ERROR = 'ABORT_STATEMENT';
    ''',
    dag=dag
)

# Execução DBT
run_dbt_deps = BashOperator(
    task_id='run_dbt_deps',
    bash_command='cd /opt/airflow/dbt/spotify_dbt && dbt deps',
    dag=dag
)

run_dbt_staging = BashOperator(
    task_id='run_dbt_staging',
    bash_command='cd /opt/airflow/dbt/spotify_dbt && dbt run --models staging.*',
    dag=dag
)

run_dbt_silver = BashOperator(
    task_id='run_dbt_silver',
    bash_command='cd /opt/airflow/dbt/spotify_dbt && dbt run --models silver.*',
    dag=dag
)

run_dbt_gold = BashOperator(
    task_id='run_dbt_gold',
    bash_command='cd /opt/airflow/dbt/spotify_dbt && dbt run --models gold.*',
    dag=dag
)

run_dbt_tests = BashOperator(
    task_id='run_dbt_tests',
    bash_command='cd /opt/airflow/dbt/spotify_dbt && dbt test',
    dag=dag
)

run_dbt_docs = BashOperator(
    task_id='run_dbt_docs',
    bash_command='cd /opt/airflow/dbt/spotify_dbt && dbt docs generate',
    dag=dag
)

# Quality Checks
data_quality_checks = SnowflakeOperator(
    task_id='data_quality_checks',
    sql='''
    -- Verificar se há dados nas camadas
    CALL SPOTIFY_ANALYTICS.GOLD.CHECK_DATA_QUALITY();
    
    -- Log de métricas
    INSERT INTO SPOTIFY_ANALYTICS.MONITORING.PIPELINE_RUNS (
        run_id, dag_name, execution_date, bronze_count, silver_count, gold_count, success
    )
    SELECT 
        '{{ ds_nodash }}' as run_id,
        'spotify_data_pipeline' as dag_name,
        '{{ execution_date }}' as execution_date,
        (SELECT COUNT(*) FROM SPOTIFY_ANALYTICS.BRONZE.RAW_PLAYS 
         WHERE DATE(loaded_at) = '{{ ds }}') as bronze_count,
        (SELECT COUNT(*) FROM SPOTIFY_ANALYTICS.SILVER.PLAYS 
         WHERE DATE(created_at) = '{{ ds }}') as silver_count,
        (SELECT COUNT(*) FROM SPOTIFY_ANALYTICS.GOLD.DAILY_PLAYS 
         WHERE play_date = '{{ ds }}') as gold_count,
        TRUE as success
    ''',
    dag=dag
)

# Notificações
send_success_notification = PythonOperator(
    task_id='send_success_notification',
    python_callable=send_slack_notification,
    dag=dag
)

# Fim do pipeline
end_pipeline = DummyOperator(
    task_id='end_pipeline',
    dag=dag
)

# Definir dependências
start_pipeline >> [check_kafka_health_task, check_minio_data_task, validate_snowflake_task]

[check_kafka_health_task, check_minio_data_task, validate_snowflake_task] >> create_bronze_tables

create_bronze_tables >> load_minio_to_bronze

load_minio_to_bronze >> run_dbt_deps

run_dbt_deps >> run_dbt_staging

run_dbt_staging >> run_dbt_silver

run_dbt_silver >> run_dbt_gold

run_dbt_gold >> run_dbt_tests

run_dbt_tests >> run_dbt_docs

run_dbt_docs >> data_quality_checks

data_quality_checks >> send_success_notification

send_success_notification >> end_pipeline