#!/usr/bin/env python3
"""
System Health Check for Spotify MDS Pipeline
"""

import sys
import requests
import json
from pathlib import Path

def check_service(url, name, timeout=5):
    """Check if a service is responding."""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name}: Healthy")
            return True
        else:
            print(f"⚠️ {name}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: {e}")
        return False

def main():
    """Run comprehensive system check."""
    print("🔍 Running Spotify MDS Pipeline Health Check...")
    print("=" * 50)
    
    services = {
        "Airflow Webserver": "http://localhost:8080/health",
        "Metabase": "http://localhost:3000/api/health", 
        "MinIO Console": "http://localhost:9001/minio/health/live",
        "Kafdrop": "http://localhost:9000"
    }
    
    healthy_count = 0
    total_services = len(services)
    
    for name, url in services.items():
        if check_service(url, name):
            healthy_count += 1
    
    print("=" * 50)
    print(f"📊 Result: {healthy_count}/{total_services} services healthy")
    
    if healthy_count == total_services:
        print("🎉 All systems go! Pipeline is ready.")
        return 0
    else:
        print("⚠️ Some services may need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())