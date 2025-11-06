#!/usr/bin/env python3
"""
Quick system check for Spotify MDS Pipeline - Windows Compatible
"""

import os
import subprocess
import sys
from pathlib import Path

def run_check(name, command=None, check_file=None, windows_command=None):
    """Run a system check with Windows compatibility."""
    print(f"🔍 {name}...", end=" ")
    
    try:
        # Use Windows-specific command if provided and on Windows
        if os.name == 'nt' and windows_command:
            command = windows_command
            
        if command:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ OK")
                return True
            else:
                print("❌ FAILED")
                if result.stderr.strip():
                    print(f"   Error: {result.stderr.strip()}")
                return False
                
        elif check_file:
            if Path(check_file).exists():
                print("✅ OK")
                return True
            else:
                print("❌ FAILED")
                print(f"   File not found: {check_file}")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🔧 SPOTIFY MDS PIPELINE - SYSTEM CHECK")
    print("=" * 50)
    
    checks = [
        {
            "name": "Docker", 
            "command": "docker --version",
            "windows_command": "docker --version"
        },
        {
            "name": "Docker Compose", 
            "command": "docker-compose --version",
            "windows_command": "docker-compose --version"
        },
        {
            "name": "Docker Daemon", 
            "command": "docker info",
            "windows_command": "docker info"
        },
        {
            "name": "Python 3", 
            "command": "python --version",
            "windows_command": "python --version"
        },
        {
            "name": "Pip", 
            "command": "pip --version", 
            "windows_command": "pip --version"
        },
        {
            "name": "Project Structure",
            "check_file": "docker-compose.yml"
        },
        {
            "name": "Environment File",
            "check_file": ".env"
        },
        {
            "name": "Source Directory",
            "check_file": "src"
        },
    ]
    
    all_ok = True
    for check in checks:
        if not run_check(**check):
            all_ok = False
    
    # Additional Windows-specific checks
    if os.name == 'nt':
        print("\n🔍 Windows Specific Checks...")
        windows_checks = [
            {
                "name": "Docker Desktop Running",
                "command": 'powershell "Get-Process docker -ErrorAction SilentlyContinue"',
                "windows_command": 'powershell "Get-Process docker -ErrorAction SilentlyContinue"'
            },
            {
                "name": "Required Ports Available",
                "command": 'powershell "netstat -an | Select-String \':3000|:8080|:9000|:9001|:3306\'"',
                "windows_command": 'powershell "netstat -an | Select-String \':3000|:8080|:9000|:9001|:3306\'"'
            },
        ]
        
        for check in windows_checks:
            if not run_check(**check):
                all_ok = False
    
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ All system checks passed! You can run the pipeline.")
        print("\n🚀 Next steps:")
        print("1. Run: python main.py")
        print("2. Select option 1 to start the pipeline")
        print("3. Access Metabase at http://localhost:3000")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n💡 WINDOWS TROUBLESHOOTING TIPS:")
        print("1. Make sure Docker Desktop is RUNNING (not just installed)")
        print("2. Run Docker Desktop as Administrator if having permission issues")
        print("3. Check if ports 3000, 8080, 9000, 9001, 3306 are available")
        print("4. Ensure WSL 2 is enabled in Docker Desktop settings")
        print("5. Try restarting Docker Desktop")
        print("\n🔧 QUICK FIXES:")
        print("- Run: docker-compose up -d")
        print("- Check: docker ps")
        print("- Restart Docker Desktop if services don't start")

def check_individual_files():
    """Check individual required files."""
    print("\n📁 FILE STRUCTURE CHECK:")
    print("-" * 30)
    
    required_files = [
        "docker-compose.yml",
        ".env",
        "src/",
        "src/producer/", 
        "src/consumer/",
        "database/",
    ]
    
    optional_files = [
        "src/producer/main.py",
        "src/consumer/kafka_to_minio.py", 
        "database/init.sql",
    ]
    
    all_required_ok = True
    
    print("Required Files:")
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            all_required_ok = False
    
    print("\nOptional Files:")
    for file_path in optional_files:
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ⚠️  {file_path} - Not found (may need to create)")
    
    return all_required_ok

if __name__ == "__main__":
    main()
    
    # Run additional file structure check
    file_check_ok = check_individual_files()
    
    if file_check_ok:
        print("\n🎉 All required files are present!")
    else:
        print("\n❌ Some required files are missing. Please check the structure.")