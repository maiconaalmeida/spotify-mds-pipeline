"""
Data processing utilities for Spotify play events.
"""

import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
from typing import Dict, List, Any, Optional
from io import BytesIO
import ujson

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class DataProcessor:
    """Process and transform Spotify play event data."""
    
    def __init__(self):
        self.required_fields = [
            'event_id', 'user_id', 'track_id', 'artist_id', 
            'event_timestamp', 'track_name', 'artist_name'
        ]
    
    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process and validate a single Kafka message."""
        try:
            message_data = message.get('value', {})
            
            # Validate required fields
            if not self._validate_message(message_data):
                logger.warning(f"⚠️ Invalid message skipped: {message_data.get('event_id', 'unknown')}")
                return None
            
            # Enrich message with additional fields
            enriched_message = self._enrich_message(message_data)
            
            return enriched_message
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return None
    
    def _validate_message(self, message: Dict[str, Any]) -> bool:
        """Validate message structure and required fields."""
        if not message:
            return False
        
        if settings.DATA_VALIDATION_ENABLED:
            for field in self.required_fields:
                if field not in message or not message[field]:
                    return False
        
        # Validate timestamp format
        timestamp = message.get('event_timestamp')
        if timestamp and not self._is_valid_timestamp(timestamp):
            return False
        
        return True
    
    def _is_valid_timestamp(self, timestamp: str) -> bool:
        """Validate timestamp format."""
        try:
            # Try to parse the timestamp
            if isinstance(timestamp, str):
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return True
        except (ValueError, TypeError):
            return False
    
    def _enrich_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich message with additional derived fields."""
        enriched = message.copy()
        
        # Parse timestamp
        timestamp_str = message.get('event_timestamp')
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                enriched['event_timestamp'] = timestamp.isoformat()
                
                # Add derived time fields
                enriched['event_date'] = timestamp.date().isoformat()
                enriched['event_hour'] = timestamp.hour
                enriched['event_day_of_week'] = timestamp.strftime('%A')
                enriched['is_weekend'] = timestamp.weekday() >= 5
                
            except (ValueError, TypeError):
                pass
        
        # Calculate completion percentage
        duration_ms = message.get('duration_ms')
        play_duration_ms = message.get('play_duration_ms')
        if duration_ms and play_duration_ms:
            enriched['completion_ratio'] = min(play_duration_ms / duration_ms, 1.0)
            enriched['is_completed'] = enriched['completion_ratio'] >= 0.9
        
        # Add processing metadata
        enriched['processed_at'] = datetime.now().isoformat()
        enriched['processing_id'] = f"proc_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        return enriched
    
    def batch_to_json(self, batch: List[Dict[str, Any]]) -> str:
        """Convert batch of messages to JSON string."""
        try:
            # Use ujson for faster JSON serialization
            return ujson.dumps(batch, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Error converting batch to JSON: {e}")
            return "[]"
    
    async def batch_to_parquet(self, batch: List[Dict[str, Any]]) -> bytes:
        """Convert batch of messages to Parquet format."""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(batch)
            
            # Convert timestamp columns
            timestamp_columns = ['event_timestamp', 'processed_at']
            for col in timestamp_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Convert to PyArrow Table
            table = pa.Table.from_pandas(df)
            
            # Write to Parquet in memory
            buffer = BytesIO()
            pq.write_table(table, buffer, compression='snappy')
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"❌ Error converting batch to Parquet: {e}")
            return b""
    
    def get_processing_stats(self, batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about processed batch."""
        if not batch:
            return {}
        
        df = pd.DataFrame(batch)
        
        stats = {
            'batch_size': len(batch),
            'unique_users': df['user_id'].nunique() if 'user_id' in df.columns else 0,
            'unique_tracks': df['track_id'].nunique() if 'track_id' in df.columns else 0,
            'unique_artists': df['artist_id'].nunique() if 'artist_id' in df.columns else 0,
            'avg_completion_ratio': df['completion_ratio'].mean() if 'completion_ratio' in df.columns else 0,
        }
        
        # Device distribution
        if 'device_type' in df.columns:
            device_counts = df['device_type'].value_counts().to_dict()
            stats['device_distribution'] = device_counts
        
        # Time distribution
        if 'event_hour' in df.columns:
            hour_counts = df['event_hour'].value_counts().sort_index().to_dict()
            stats['hourly_distribution'] = hour_counts
        
        return stats