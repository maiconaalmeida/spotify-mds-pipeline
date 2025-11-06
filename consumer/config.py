"""
Configuration settings for the Kafka Consumer.
"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings."""
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: List[str] = os.getenv(
        'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'
    ).split(',')
    
    KAFKA_TOPIC: str = os.getenv('KAFKA_TOPIC', 'spotify-plays')
    KAFKA_GROUP_ID: str = os.getenv('KAFKA_GROUP_ID_CONSUMER', 'spotify-consumer-group')
    KAFKA_AUTO_OFFSET_RESET: str = os.getenv('KAFKA_AUTO_OFFSET_RESET', 'earliest')
    KAFKA_ENABLE_AUTO_COMMIT: bool = os.getenv('KAFKA_ENABLE_AUTO_COMMIT', 'true').lower() == 'true'
    
    # MinIO Configuration
    MINIO_ENDPOINT: str = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
    MINIO_ACCESS_KEY: str = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
    MINIO_SECRET_KEY: str = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
    MINIO_BUCKET: str = os.getenv('MINIO_BUCKET', 'spotify-data')
    MINIO_SECURE: bool = os.getenv('MINIO_SECURE_CONNECTION', 'false').lower() == 'true'
    
    # Consumer Configuration
    CONSUMER_BATCH_SIZE: int = int(os.getenv('CONSUMER_BATCH_SIZE', '100'))
    CONSUMER_BATCH_TIMEOUT_SECONDS: int = int(os.getenv('CONSUMER_BATCH_TIMEOUT_SECONDS', '30'))
    CONSUMER_POLL_TIMEOUT_MS: int = int(os.getenv('CONSUMER_POLL_TIMEOUT_MS', '1000'))
    CONSUMER_MAX_RETRY_ATTEMPTS: int = int(os.getenv('CONSUMER_MAX_RETRY_ATTEMPTS', '3'))
    
    # Data Processing
    DATA_VALIDATION_ENABLED: bool = os.getenv('DATA_VALIDATION_ENABLED', 'true').lower() == 'true'
    
    # Logging
    LOG_LEVEL: str = os.getenv('APP_LOG_LEVEL', 'INFO')
    
    # Health Check
    HEALTH_CHECK_PORT: int = int(os.getenv('HEALTH_CHECK_PORT', '8080'))

settings = Settings()