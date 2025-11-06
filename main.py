#!/usr/bin/env python3
"""
Simplified Pipeline Starter - Fix Docker Compose Issues
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def run_command(command, description):
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Success")
            return True
        else:
            print(f"❌ Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_docker_compose_file():
    """Check and fix docker-compose.yml"""
    compose_file = Path("docker-compose.yml")
    
    if not compose_file.exists():
        print("❌ docker-compose.yml not found!")
        return False
        
    # Read current content
    with open(compose_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove version line if exists
    if content.startswith('version:'):
        lines = content.split('\n')
        # Skip the version line
        new_content = '\n'.join(lines[1:])
        
        with open(compose_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Removed obsolete 'version' line from docker-compose.yml")
    
    return True

def main():
    print("🎵 SPOTIFY MDS PIPELINE - FIXED VERSION")
    print("=" * 50)
    
    # Step 1: Fix docker-compose.yml
    if not check_docker_compose_file():
        print("❌ Cannot fix docker-compose.yml")
        return
    
    # Step 2: Stop any running services
    print("\n1. Cleaning up existing services...")
    run_command("docker-compose down", "Stopping existing services")
    
    # Step 3: Start services
    print("\n2. Starting services...")
    if run_command("docker-compose up -d", "Starting Docker services"):
        print("✅ Services started successfully!")
        
        # Step 4: Wait for services
        print("\n3. Waiting for services to be ready...")
        print("⏳ This may take 2-3 minutes...")
        
        for i in range(12):  # Wait up to 2 minutes
            print(f"⏰ Waiting... ({i*10}s)")
            time.sleep(10)
            
            # Check if Airflow is responding
            try:
                import requests
                response = requests.get("http://localhost:8080/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Airflow is ready!")
                    break
            except:
                pass
                
        # Step 5: Show status
        print("\n4. Final Status:")
        run_command("docker-compose ps", "Service status")
        
        print("\n🌐 ACCESS URLs:")
        print("Airflow: http://localhost:8080 (admin/admin123)")
        print("Metabase: http://localhost:3000")
        print("MinIO: http://localhost:9001 (minioadmin/minioadmin123)")
        print("Kafdrop: http://localhost:9000")
        
    else:
        print("❌ Failed to start services")

if __name__ == "__main__":
    main()