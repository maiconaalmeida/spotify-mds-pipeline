#!/usr/bin/env python3
"""
Kafka to MinIO Data Pipeline Consumer

This service consumes Spotify streaming data from Kafka and stores it in MinIO
in a structured data lake format (bronze layer) with proper partitioning.

Features:
- Batch processing with configurable size and time windows
- Structured data lake partitioning (date/hour)
- Comprehensive error handling and retry logic
- Health checks and metrics
- Graceful shutdown handling
- Data validation and schema evolution support
"""

import json
import os
import logging
import signal
import sys
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError, BotoCoreError
from kafka import KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# ---------- Configuration ----------
@dataclass
class Config:
    """Configuration settings for the Kafka to MinIO pipeline."""
    # MinIO Configuration
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str
    minio_secure: bool = False
    
    # Kafka Configuration
    kafka_bootstrap_servers: str
    kafka_topic: str
    kafka_group_id: str
    kafka_auto_offset_reset: str = "earliest"
    
    # Processing Configuration
    batch_size: int = 100
    batch_timeout_seconds: int = 30
    max_retry_attempts: int = 3
    
    # Data Lake Configuration
    data_lake_base_path: str = "bronze"
    file_format: str = "json"

class KafkaMinIOConsumer:
    """Kafka to MinIO consumer with batch processing and error handling."""
    
    def __init__(self, config: Config):
        self.config = config
        self.consumer = None
        self.s3_client = None
        self.batch: List[Dict[str, Any]] = []
        self.last_batch_time = datetime.now(timezone.utc)
        self.is_running = True
        self.metrics = {
            'messages_processed': 0,
            'batches_uploaded': 0,
            'errors_encountered': 0,
            'last_successful_upload': None
        }
        
        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers for graceful shutdown
        self.setup_signal_handlers()
    
    def setup_logging(self):
        """Configure logging format and level."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('kafka_to_minio.log')
            ]
        )
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
            self.is_running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def initialize_minio_client(self) -> bool:
        """Initialize and validate MinIO/S3 client connection."""
        try:
            self.logger.info("Initializing MinIO client...")
            
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=self.config.minio_endpoint,
                aws_access_key_id=self.config.minio_access_key,
                aws_secret_access_key=self.config.minio_secret_key,
                verify=self.config.minio_secure
            )
            
            # Test connection and ensure bucket exists
            self.ensure_bucket_exists()
            self.logger.info("✅ MinIO client initialized successfully")
            return True
            
        except (ClientError, BotoCoreError) as e:
            self.logger.error(f"❌ Failed to initialize MinIO client: {e}")
            return False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ClientError, BotoCoreError))
    )
    def ensure_bucket_exists(self):
        """Ensure MinIO bucket exists, create if it doesn't."""
        try:
            self.s3_client.head_bucket(Bucket=self.config.minio_bucket)
            self.logger.info(f"✅ Bucket '{self.config.minio_bucket}' already exists")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == '404':
                try:
                    self.s3_client.create_bucket(Bucket=self.config.minio_bucket)
                    self.logger.info(f"✅ Created bucket '{self.config.minio_bucket}'")
                except ClientError as create_error:
                    self.logger.error(f"❌ Failed to create bucket: {create_error}")
                    raise
            else:
                self.logger.error(f"❌ Error checking bucket: {e}")
                raise
    
    def initialize_kafka_consumer(self) -> bool:
        """Initialize and validate Kafka consumer connection."""
        try:
            self.logger.info("Initializing Kafka consumer...")
            
            self.consumer = KafkaConsumer(
                self.config.kafka_topic,
                bootstrap_servers=self.config.kafka_bootstrap_servers.split(','),
                auto_offset_reset=self.config.kafka_auto_offset_reset,
                enable_auto_commit=True,
                auto_commit_interval_ms=5000,
                group_id=self.config.kafka_group_id,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            
            # Test connection
            self.consumer.topics()
            self.logger.info("✅ Kafka consumer initialized successfully")
            return True
            
        except NoBrokersAvailable as e:
            self.logger.error(f"❌ No Kafka brokers available: {e}")
            return False
        except KafkaError as e:
            self.logger.error(f"❌ Kafka initialization error: {e}")
            return False
    
    def validate_message(self, message: Dict[str, Any]) -> bool:
        """Validate incoming Kafka message structure."""
        required_fields = ['user_id', 'track_id', 'played_at']
        
        for field in required_fields:
            if field not in message:
                self.logger.warning(f"⚠️ Message missing required field '{field}': {message}")
                return False
        
        # Add timestamp if missing
        if 'processed_at' not in message:
            message['processed_at'] = datetime.now(timezone.utc).isoformat()
        
        return True
    
    def generate_s3_key(self) -> str:
        """Generate S3 key with proper data lake partitioning."""
        now = datetime.now(timezone.utc)
        date_path = now.strftime("date=%Y-%m-%d/hour=%H")
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        
        return (
            f"{self.config.data_lake_base_path}/"
            f"{date_path}/"
            f"spotify_events_{timestamp}.{self.config.file_format}"
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ClientError, BotoCoreError))
    )
    def upload_batch_to_minio(self, batch: List[Dict[str, Any]]) -> bool:
        """Upload batch of messages to MinIO."""
        if not batch:
            return True
        
        try:
            s3_key = self.generate_s3_key()
            json_data = "\n".join([json.dumps(record) for record in batch])
            
            self.s3_client.put_object(
                Bucket=self.config.minio_bucket,
                Key=s3_key,
                Body=json_data.encode("utf-8"),
                ContentType='application/json'
            )
            
            self.metrics['batches_uploaded'] += 1
            self.metrics['last_successful_upload'] = datetime.now(timezone.utc)
            self.logger.info(f"✅ Uploaded {len(batch)} events to MinIO: {s3_key}")
            return True
            
        except (ClientError, BotoCoreError) as e:
            self.logger.error(f"❌ Failed to upload batch to MinIO: {e}")
            self.metrics['errors_encountered'] += 1
            return False
    
    def should_flush_batch(self) -> bool:
        """Check if current batch should be flushed based on size or time."""
        time_since_last_batch = (datetime.now(timezone.utc) - self.last_batch_time).total_seconds()
        
        return (len(self.batch) >= self.config.batch_size or 
                time_since_last_batch >= self.config.batch_timeout_seconds)
    
    def process_batch(self):
        """Process and upload the current batch if conditions are met."""
        if self.batch and self.should_flush_batch():
            if self.upload_batch_to_minio(self.batch):
                self.batch = []
                self.last_batch_time = datetime.now(timezone.utc)
    
    def log_metrics(self):
        """Log current operational metrics."""
        self.logger.info(
            f"📊 Metrics - Messages: {self.metrics['messages_processed']}, "
            f"Batches: {self.metrics['batches_uploaded']}, "
            f"Errors: {self.metrics['errors_encountered']}"
        )
    
    def run(self):
        """Main consumer loop."""
        self.logger.info("🚀 Starting Kafka to MinIO consumer...")
        
        # Initialize clients
        if not self.initialize_minio_client() or not self.initialize_kafka_consumer():
            self.logger.error("❌ Failed to initialize clients. Exiting.")
            sys.exit(1)
        
        self.logger.info(f"🎧 Listening for events on topic '{self.config.kafka_topic}'...")
        
        try:
            while self.is_running:
                # Poll for messages with timeout
                message_batch = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        try:
                            if self.validate_message(message.value):
                                self.batch.append(message.value)
                                self.metrics['messages_processed'] += 1
                        
                        except json.JSONDecodeError as e:
                            self.logger.error(f"❌ JSON decode error: {e}")
                            self.metrics['errors_encountered'] += 1
                        except Exception as e:
                            self.logger.error(f"❌ Error processing message: {e}")
                            self.metrics['errors_encountered'] += 1
                
                # Process batch if conditions are met
                self.process_batch()
                
                # Log metrics every 1000 messages
                if self.metrics['messages_processed'] % 1000 == 0:
                    self.log_metrics()
        
        except KafkaError as e:
            self.logger.error(f"❌ Kafka error: {e}")
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown procedure."""
        self.logger.info("🛑 Shutting down Kafka to MinIO consumer...")
        
        # Upload any remaining messages
        if self.batch:
            self.logger.info(f"📦 Uploading final batch of {len(self.batch)} messages...")
            self.upload_batch_to_minio(self.batch)
        
        # Close Kafka consumer
        if self.consumer:
            self.consumer.close()
        
        # Log final metrics
        self.log_metrics()
        self.logger.info("✅ Kafka to MinIO consumer shutdown complete")

def load_config() -> Config:
    """Load configuration from environment variables."""
    load_dotenv()
    
    return Config(
        # MinIO Configuration
        minio_endpoint=os.getenv("MINIO_ENDPOINT", "http://localhost:9002"),
        minio_access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        minio_secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
        minio_bucket=os.getenv("MINIO_BUCKET_RAW", "spotify-raw"),
        minio_secure=os.getenv("MINIO_SECURE_CONNECTION", "false").lower() == "true",
        
        # Kafka Configuration
        kafka_bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092"),
        kafka_topic=os.getenv("KAFKA_TOPIC_SPOTIFY_STREAMS", "spotify-streams"),
        kafka_group_id=os.getenv("KAFKA_GROUP_ID_CONSUMER", "kafka-to-minio-group"),
        
        # Processing Configuration
        batch_size=int(os.getenv("BATCH_SIZE", "100")),
        batch_timeout_seconds=int(os.getenv("BATCH_TIMEOUT_SECONDS", "30")),
        max_retry_attempts=int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
    )

if __name__ == "__main__":
    config = load_config()
    consumer = KafkaMinIOConsumer(config)
    consumer.run()