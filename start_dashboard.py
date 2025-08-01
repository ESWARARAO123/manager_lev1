#!/usr/bin/env python3.12
"""
Simple launcher for RHEL Resource Manager Web Dashboard
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Launch the web dashboard"""
    try:
        from web_dashboard import start_dashboard
        print("🚀 Starting RHEL Resource Manager Web Dashboard...")
        print("📊 This will open a web browser with the live dashboard")
        print("⏱️  Dashboard updates every 5 seconds automatically")
        print("🔄 Press Ctrl+C to stop the dashboard")
        print()
        
        start_dashboard()
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Make sure all required packages are installed:")
        print("  pip install plotly psutil pandas")
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    main() 