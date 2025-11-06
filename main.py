#!/usr/bin/env python3
"""
Spotify MDS Pipeline - Windows Compatible Version
"""

import os
import sys
import time
import subprocess
from pathlib import Path

class SimplePipelineManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        
    def run_command(self, command, check_output=False):
        """Run command and return success status."""
        try:
            print(f"🚀 Running: {command}")
            result = subprocess.run(command, shell=True, cwd=self.base_dir, 
                                  capture_output=check_output, text=check_output)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
            
    def check_docker_services(self):
        """Check if Docker services are running."""
        print("🔍 Checking Docker services...")
        return self.run_command("docker-compose ps")
        
    def start_docker_services(self):
        """Start all Docker services."""
        print("🐳 Starting Docker services...")
        if self.run_command("docker-compose up -d"):
            print("⏳ Waiting for services to start...")
            time.sleep(15)
            return self.check_docker_services()
        return False
        
    def stop_docker_services(self):
        """Stop all Docker services."""
        print("🛑 Stopping Docker services...")
        return self.run_command("docker-compose down")
        
    def start_producer(self):
        """Start the data producer."""
        print("🎵 Starting data producer...")
        producer_script = self.base_dir / "src" / "producer" / "main.py"
        if producer_script.exists():
            return self.run_command(f'python "{producer_script}"', check_output=False)
        else:
            print(f"❌ Producer script not found: {producer_script}")
            return False
            
    def start_consumer(self):
        """Start the data consumer."""
        print("📥 Starting data consumer...")
        consumer_script = self.base_dir / "src" / "consumer" / "kafka_to_minio.py"
        if consumer_script.exists():
            return self.run_command(f'python "{consumer_script}"', check_output=False)
        else:
            print(f"❌ Consumer script not found: {consumer_script}")
            return False
            
    def show_status(self):
        """Show service status."""
        print("\n" + "="*50)
        print("🔄 SERVICE STATUS")
        print("="*50)
        self.run_command("docker-compose ps")
        print("="*50)
        
    def show_urls(self):
        """Show important URLs."""
        print("\n🌐 IMPORTANT URLs:")
        print("Metabase Dashboard: http://localhost:3000")
        print("Airflow UI: http://localhost:8080")
        print("Kafdrop (Kafka UI): http://localhost:9000")
        print("MinIO Console: http://localhost:9001")
        print("\n🔐 Default Credentials:")
        print("Metabase: admin@spotify-analytics.com / admin123")
        print("Airflow: admin / admin123")
        print("MinIO: minioadmin / minioadmin123")
        
    def start_all(self):
        """Start the entire pipeline."""
        print("🎵 Starting Spotify MDS Pipeline...")
        
        if not self.start_docker_services():
            print("❌ Failed to start Docker services")
            return False
            
        print("✅ Docker services started successfully!")
        
        # Start producer and consumer
        print("\nStarting data processing components...")
        self.start_producer()
        self.start_consumer()
        
        print("\n✅ Pipeline started successfully!")
        self.show_urls()
        return True
        
    def stop_all(self):
        """Stop the entire pipeline."""
        print("🛑 Stopping Spotify MDS Pipeline...")
        self.stop_docker_services()
        print("✅ Pipeline stopped!")
        
    def interactive_menu(self):
        """Simple interactive menu."""
        while True:
            print("\n" + "="*50)
            print("🎵 SPOTIFY MDS PIPELINE - WINDOWS VERSION")
            print("="*50)
            print("1. 🚀 Start Entire Pipeline")
            print("2. 🛑 Stop Entire Pipeline")
            print("3. 🔄 Show Status")
            print("4. 🌐 Show URLs")
            print("5. ❌ Exit")
            print("="*50)
            
            choice = input("Select option (1-5): ").strip()
            
            if choice == '1':
                if self.start_all():
                    input("\n✅ Success! Press Enter to continue...")
                else:
                    input("\n❌ Failed! Press Enter to continue...")
                    
            elif choice == '2':
                self.stop_all()
                input("\n🛑 Stopped! Press Enter to continue...")
                
            elif choice == '3':
                self.show_status()
                input("\nPress Enter to continue...")
                
            elif choice == '4':
                self.show_urls()
                input("\nPress Enter to continue...")
                
            elif choice == '5':
                print("\n👋 Thank you for using Spotify MDS Pipeline!")
                break
                
            else:
                print("❌ Invalid option. Please try again.")

def main():
    """Main entry point."""
    # Check if we're on Windows
    if os.name != 'nt':
        print("⚠️ This version is optimized for Windows.")
        print("For Linux/Mac, use the standard main.py")
        
    manager = SimplePipelineManager()
    manager.interactive_menu()

if __name__ == "__main__":
    main()