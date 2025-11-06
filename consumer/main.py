#!/usr/bin/env python3
"""
Kafka Consumer for Spotify Data Pipeline
=======================================
Consume Spotify play events from Kafka and store in MinIO as JSON/Parquet files.
"""

import asyncio
import signal
import sys
import time
from datetime import datetime
from typing import Dict, List, Any
import json

from kafka_consumer import SpotifyKafkaConsumer
from minio_client import MinIOClient
from data_processor import DataProcessor
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class SpotifyDataConsumer:
    def __init__(self):
        """Initialize the Spotify data consumer."""
        self.consumer = SpotifyKafkaConsumer()
        self.minio_client = MinIOClient()
        self.data_processor = DataProcessor()
        self.is_running = False
        self.stats = {
            'messages_processed': 0,
            'batches_saved': 0,
            'errors': 0,
            'start_time': None
        }
        
    async def start(self):
        """Start the consumer service."""
        logger.info("🎵 Starting Spotify Data Consumer...")
        
        # Initialize clients
        await self.minio_client.initialize()
        await self.consumer.initialize()
        
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        
        logger.info("✅ Consumer started successfully")
        logger.info(f"📊 Configuration: batch_size={settings.CONSUMER_BATCH_SIZE}, "
                   f"timeout={settings.CONSUMER_BATCH_TIMEOUT_SECONDS}s")
        
        # Start consuming messages
        await self._consume_loop()
    
    async def stop(self):
        """Stop the consumer service gracefully."""
        logger.info("🛑 Stopping Spotify Data Consumer...")
        self.is_running = False
        await self.consumer.close()
        logger.info("✅ Consumer stopped gracefully")
    
    async def _consume_loop(self):
        """Main consumption loop."""
        batch = []
        last_batch_time = time.time()
        
        while self.is_running:
            try:
                # Poll for messages
                messages = await self.consumer.poll_messages(
                    timeout_ms=settings.CONSUMER_POLL_TIMEOUT_MS
                )
                
                if messages:
                    processed_messages = await self._process_messages(messages)
                    batch.extend(processed_messages)
                    self.stats['messages_processed'] += len(processed_messages)
                
                # Check if we should save the batch
                current_time = time.time()
                time_elapsed = current_time - last_batch_time
                batch_full = len(batch) >= settings.CONSUMER_BATCH_SIZE
                timeout_reached = time_elapsed >= settings.CONSUMER_BATCH_TIMEOUT_SECONDS
                
                if batch and (batch_full or timeout_reached):
                    await self._save_batch(batch)
                    batch.clear()
                    last_batch_time = current_time
                
                # Small sleep to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Error in consumption loop: {e}")
                self.stats['errors'] += 1
                await asyncio.sleep(1)  # Backoff on error
    
    async def _process_messages(self, messages: List[Dict]) -> List[Dict]:
        """Process raw Kafka messages."""
        processed_messages = []
        
        for message in messages:
            try:
                # Validate and enrich message
                processed_message = self.data_processor.process_message(message)
                if processed_message:
                    processed_messages.append(processed_message)
                    
                    # Log progress periodically
                    if self.stats['messages_processed'] % 100 == 0:
                        logger.info(f"📥 Processed {self.stats['messages_processed']} messages")
                        
            except Exception as e:
                logger.error(f"❌ Error processing message: {e}")
                self.stats['errors'] += 1
        
        return processed_messages
    
    async def _save_batch(self, batch: List[Dict]):
        """Save a batch of messages to MinIO."""
        if not batch:
            return
            
        try:
            logger.info(f"💾 Saving batch of {len(batch)} messages to MinIO...")
            
            # Convert batch to different formats
            json_data = self.data_processor.batch_to_json(batch)
            parquet_data = await self.data_processor.batch_to_parquet(batch)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            json_filename = f"raw/spotify_plays_{timestamp}.json"
            parquet_filename = f"processed/spotify_plays_{timestamp}.parquet"
            
            # Save to MinIO
            await self.minio_client.upload_json(
                data=json_data,
                filename=json_filename
            )
            
            await self.minio_client.upload_parquet(
                data=parquet_data,
                filename=parquet_filename
            )
            
            self.stats['batches_saved'] += 1
            logger.info(f"✅ Batch saved: {json_filename}, {parquet_filename}")
            
        except Exception as e:
            logger.error(f"❌ Error saving batch to MinIO: {e}")
            self.stats['errors'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get consumer statistics."""
        if self.stats['start_time']:
            elapsed = datetime.now() - self.stats['start_time']
            self.stats['uptime_seconds'] = elapsed.total_seconds()
            self.stats['messages_per_second'] = (
                self.stats['messages_processed'] / elapsed.total_seconds() 
                if elapsed.total_seconds() > 0 else 0
            )
        return self.stats.copy()

async def main():
    """Main application entry point."""
    consumer = SpotifyDataConsumer()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(consumer.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await consumer.start()
    except Exception as e:
        logger.error(f"❌ Failed to start consumer: {e}")
        sys.exit(1)
    finally:
        # Print final statistics
        stats = consumer.get_stats()
        logger.info("📊 Final Statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())