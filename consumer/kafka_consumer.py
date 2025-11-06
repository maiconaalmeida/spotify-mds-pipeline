"""
Kafka Consumer for Spotify play events.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from kafka import KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class SpotifyKafkaConsumer:
    """Kafka consumer for Spotify play events."""
    
    def __init__(self):
        self.consumer: Optional[KafkaConsumer] = None
        self.is_connected = False
    
    async def initialize(self, retry_attempts: int = None):
        """Initialize Kafka consumer with retry logic."""
        retry_attempts = retry_attempts or settings.CONSUMER_MAX_RETRY_ATTEMPTS
        
        for attempt in range(retry_attempts):
            try:
                logger.info(f"🔌 Connecting to Kafka (attempt {attempt + 1}/{retry_attempts})...")
                
                self.consumer = KafkaConsumer(
                    settings.KAFKA_TOPIC,
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    group_id=settings.KAFKA_GROUP_ID,
                    auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
                    enable_auto_commit=settings.KAFKA_ENABLE_AUTO_COMMIT,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
                    key_deserializer=lambda x: x.decode('utf-8') if x else None,
                    max_poll_records=500,
                    session_timeout_ms=30000,
                    heartbeat_interval_ms=10000
                )
                
                # Test connection by getting topic metadata
                self.consumer.topics()
                self.is_connected = True
                
                logger.info("✅ Successfully connected to Kafka")
                logger.info(f"📡 Subscribed to topic: {settings.KAFKA_TOPIC}")
                logger.info(f"👥 Consumer group: {settings.KAFKA_GROUP_ID}")
                return
                
            except NoBrokersAvailable as e:
                logger.warning(f"⚠️ Kafka brokers not available: {e}")
                if attempt < retry_attempts - 1:
                    wait_time = (attempt + 1) * 5  # Exponential backoff
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("❌ Failed to connect to Kafka after all retry attempts")
                    raise
                    
            except KafkaError as e:
                logger.error(f"❌ Kafka error during initialization: {e}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(5)
                else:
                    raise
    
    async def poll_messages(self, timeout_ms: int = 1000) -> List[Dict[str, Any]]:
        """Poll for new messages from Kafka."""
        if not self.is_connected or not self.consumer:
            raise RuntimeError("Kafka consumer not initialized")
        
        try:
            # Poll for messages
            raw_messages = self.consumer.poll(timeout_ms=timeout_ms)
            messages = []
            
            for topic_partition, partition_messages in raw_messages.items():
                for message in partition_messages:
                    if message.value:
                        messages.append({
                            'value': message.value,
                            'key': message.key,
                            'topic': message.topic,
                            'partition': message.partition,
                            'offset': message.offset,
                            'timestamp': message.timestamp,
                            'headers': dict(message.headers) if message.headers else {}
                        })
            
            return messages
            
        except KafkaError as e:
            logger.error(f"❌ Error polling messages from Kafka: {e}")
            self.is_connected = False
            raise
    
    async def commit_offsets(self):
        """Commit current offsets to Kafka."""
        if self.consumer and self.is_connected:
            try:
                self.consumer.commit()
                logger.debug("✅ Offsets committed successfully")
            except KafkaError as e:
                logger.error(f"❌ Error committing offsets: {e}")
    
    async def get_consumer_metrics(self) -> Dict[str, Any]:
        """Get consumer metrics and statistics."""
        if not self.consumer:
            return {}
        
        try:
            metrics = self.consumer.metrics()
            assignment = self.consumer.assignment()
            
            return {
                'metrics': metrics,
                'assignment': [str(tp) for tp in assignment],
                'connected': self.is_connected
            }
        except Exception as e:
            logger.error(f"❌ Error getting consumer metrics: {e}")
            return {}
    
    async def close(self):
        """Close the Kafka consumer gracefully."""
        if self.consumer:
            try:
                # Commit final offsets
                await self.commit_offsets()
                self.consumer.close()
                self.is_connected = False
                logger.info("✅ Kafka consumer closed gracefully")
            except Exception as e:
                logger.error(f"❌ Error closing Kafka consumer: {e}")