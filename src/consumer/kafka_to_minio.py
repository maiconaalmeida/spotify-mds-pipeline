#!/usr/bin/env python3
"""
Simple Kafka to MinIO Consumer
"""

import json
import os
from datetime import datetime
from kafka import KafkaConsumer
import boto3

# Configuration
MINIO_ENDPOINT = "http://localhost:9002"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin123"
MINIO_BUCKET = "spotify-raw"

# Create MinIO client
s3 = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY
)

# Ensure bucket exists
try:
    s3.create_bucket(Bucket=MINIO_BUCKET)
    print(f"✅ Created bucket: {MINIO_BUCKET}")
except:
    print(f"✅ Bucket already exists: {MINIO_BUCKET}")

# Create Kafka consumer
consumer = KafkaConsumer(
    'spotify-streams',
    bootstrap_servers=['localhost:29092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("🎧 Listening for Spotify events...")

batch = []
BATCH_SIZE = 10

for message in consumer:
    event = message.value
    batch.append(event)
    
    if len(batch) >= BATCH_SIZE:
        # Create file path with date partitioning
        now = datetime.now()
        date_path = now.strftime("year=%Y/month=%m/day=%d")
        filename = f"spotify_events_{now.strftime('%H%M%S')}.json"
        s3_key = f"bronze/{date_path}/{filename}"
        
        # Convert batch to JSON lines
        json_data = "\n".join([json.dumps(e, ensure_ascii=False) for e in batch])
        
        # Upload to MinIO
        try:
            s3.put_object(
                Bucket=MINIO_BUCKET,
                Key=s3_key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json'
            )
            print(f"💾 Saved {len(batch)} events to: {s3_key}")
            batch = []
        except Exception as e:
            print(f"❌ Failed to upload to MinIO: {e}")
print(f"❌ Failed to upload to MinIO: {e}")