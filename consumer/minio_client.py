"""
MinIO client for storing Spotify data.
"""

import asyncio
import io
from typing import Dict, Any, Optional
from minio import Minio
from minio.error import S3Error

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class MinIOClient:
    """MinIO client for storing Spotify data in various formats."""
    
    def __init__(self):
        self.client: Optional[Minio] = None
        self.is_connected = False
    
    async def initialize(self):
        """Initialize MinIO client and ensure bucket exists."""
        try:
            logger.info("🔌 Connecting to MinIO...")
            
            self.client = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            
            # Test connection
            self.client.list_buckets()
            self.is_connected = True
            
            # Ensure bucket exists
            await self._ensure_bucket_exists(settings.MINIO_BUCKET)
            
            logger.info("✅ Successfully connected to MinIO")
            logger.info(f"📦 Using bucket: {settings.MINIO_BUCKET}")
            
        except S3Error as e:
            logger.error(f"❌ MinIO connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to MinIO: {e}")
            raise
    
    async def _ensure_bucket_exists(self, bucket_name: str):
        """Ensure the bucket exists, create if it doesn't."""
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"✅ Created bucket: {bucket_name}")
            else:
                logger.info(f"✅ Bucket already exists: {bucket_name}")
        except S3Error as e:
            logger.error(f"❌ Error ensuring bucket exists: {e}")
            raise
    
    async def upload_json(self, data: str, filename: str):
        """Upload JSON data to MinIO."""
        if not self.is_connected or not self.client:
            raise RuntimeError("MinIO client not initialized")
        
        try:
            # Convert string to bytes
            data_bytes = data.encode('utf-8')
            data_stream = io.BytesIO(data_bytes)
            
            # Upload to MinIO
            self.client.put_object(
                bucket_name=settings.MINIO_BUCKET,
                object_name=filename,
                data=data_stream,
                length=len(data_bytes),
                content_type='application/json'
            )
            
            logger.debug(f"✅ JSON uploaded: {filename}")
            
        except S3Error as e:
            logger.error(f"❌ Error uploading JSON to MinIO: {e}")
            raise
    
    async def upload_parquet(self, data: bytes, filename: str):
        """Upload Parquet data to MinIO."""
        if not self.is_connected or not self.client:
            raise RuntimeError("MinIO client not initialized")
        
        try:
            data_stream = io.BytesIO(data)
            
            self.client.put_object(
                bucket_name=settings.MINIO_BUCKET,
                object_name=filename,
                data=data_stream,
                length=len(data),
                content_type='application/parquet'
            )
            
            logger.debug(f"✅ Parquet uploaded: {filename}")
            
        except S3Error as e:
            logger.error(f"❌ Error uploading Parquet to MinIO: {e}")
            raise
    
    async def list_files(self, prefix: str = "") -> list:
        """List files in MinIO bucket with given prefix."""
        if not self.is_connected or not self.client:
            return []
        
        try:
            objects = self.client.list_objects(
                bucket_name=settings.MINIO_BUCKET,
                prefix=prefix,
                recursive=True
            )
            
            return [obj.object_name for obj in objects]
            
        except S3Error as e:
            logger.error(f"❌ Error listing files in MinIO: {e}")
            return []
    
    async def get_bucket_stats(self) -> Dict[str, Any]:
        """Get statistics about the MinIO bucket."""
        if not self.is_connected or not self.client:
            return {}
        
        try:
            objects = list(self.client.list_objects(
                bucket_name=settings.MINIO_BUCKET,
                recursive=True
            ))
            
            total_size = sum(obj.size for obj in objects)
            file_count = len(objects)
            
            return {
                'file_count': file_count,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'objects': [obj.object_name for obj in objects[:10]]  # First 10 objects
            }
            
        except S3Error as e:
            logger.error(f"❌ Error getting bucket stats: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """Perform health check on MinIO connection."""
        try:
            if self.client and self.is_connected:
                self.client.list_buckets()
                return True
            return False
        except Exception:
            self.is_connected = False
            return False