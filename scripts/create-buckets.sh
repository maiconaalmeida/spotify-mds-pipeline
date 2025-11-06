#!/bin/bash
# Script para criar buckets no MinIO

until mc alias set myminio http://minio:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}; do
  echo "⌛ Waiting for MinIO..."
  sleep 2
done

mc mb myminio/spotify-data --ignore-existing
mc mb myminio/spotify-backups --ignore-existing
mc anonymous set public myminio/spotify-data

echo "✅ MinIO buckets created successfully"