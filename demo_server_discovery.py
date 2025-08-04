#!/usr/bin/env python3.12
"""
Server Discovery Demo
Demonstrates the new server discovery and management features
"""

import sys
import os
import time
import requests
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_server_discovery():
    """Demonstrate server discovery features"""
    print("🚀 Server Discovery and Management Demo")
    print("=" * 50)
    print()
    
    # Check if dashboard is running
    try:
        response = requests.get('http://localhost:8005/api/server-status', timeout=5)
        if response.status_code == 200:
            print("✅ Web dashboard is running on http://localhost:8005")
        else:
            print("❌ Web dashboard is not responding properly")
            return
    except requests.exceptions.RequestException:
        print("❌ Web dashboard is not running. Please start it first:")
        print("   python3 web_dashboard.py")
        return
    
    print()
    print("📋 Available Features:")
    print("1. 🔍 Network Discovery - Scan for servers in your network")
    print("2. 🔗 SSH Connection Management - Connect to servers via SSH")
    print("3. 📊 Multi-Server Monitoring - Monitor all connected servers")
    print("4. 💾 Configuration Persistence - Save/load server configurations")
    print()
    
    # Test server status API
    print("🔍 Testing Server Status API...")
    try:
        response = requests.get('http://localhost:8005/api/server-status')
        data = response.json()
        
        if data['success']:
            status = data['status']
            print(f"✅ Server discovery status:")
            print(f"   - Scanning: {status['scanning']}")
            print(f"   - Discovered servers: {status['discovered_count']}")
            print(f"   - Connected servers: {status['connected_count']}")
            print(f"   - Network ranges: {', '.join(status['network_ranges'])}")
        else:
            print(f"❌ Error: {data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error testing API: {e}")
    
    print()
    print("🌐 Web Interface Instructions:")
    print("1. Open your browser and go to: http://localhost:8005")
    print("2. Click the '⚙️ Settings' button in the top-right corner")
    print("3. Use the Network Discovery section to scan for servers")
    print("4. Connect to discovered servers using SSH credentials")
    print("5. Monitor all connected servers from the main dashboard")
    print()
    
    # Test network scanning
    print("🔍 Testing Network Scanning...")
    try:
        print("Starting network scan (this may take a few minutes)...")
        response = requests.post('http://localhost:8005/api/scan-network')
        data = response.json()
        
        if data['success']:
            print(f"✅ Network scan started successfully")
            print(f"   - Message: {data['message']}")
            print(f"   - Currently discovered: {data['discovered_count']} servers")
            
            # Wait a bit and check status again
            print("⏱️  Waiting for scan to complete...")
            time.sleep(10)
            
            response = requests.get('http://localhost:8005/api/server-status')
            data = response.json()
            
            if data['success']:
                status = data['status']
                print(f"📊 Scan status after 10 seconds:")
                print(f"   - Scanning: {status['scanning']}")
                print(f"   - Discovered servers: {status['discovered_count']}")
                
                if status['discovered_servers']:
                    print("   - Discovered servers:")
                    for ip in status['discovered_servers']:
                        print(f"     📡 {ip}")
                else:
                    print("   - No servers discovered yet (scan may still be running)")
        else:
            print(f"❌ Scan failed: {data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error during network scan: {e}")
    
    print()
    print("🔗 SSH Connection Demo:")
    print("To connect to a server via SSH:")
    print("1. Use the web interface settings modal")
    print("2. Or use the API directly:")
    print()
    print("Example API call:")
    print("curl -X POST http://localhost:8005/api/connect-server \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"ip\": \"172.16.16.23\", \"username\": \"root\", \"password\": \"your_password\"}'")
    print()
    
    print("💾 Configuration Management:")
    print("Save configuration:")
    print("curl -X POST http://localhost:8005/api/save-config")
    print()
    print("Load configuration:")
    print("curl -X POST http://localhost:8005/api/load-config")
    print()
    
    print("🎉 Demo completed!")
    print("💡 Open http://localhost:8005 in your browser to use the full interface")

if __name__ == "__main__":
    demo_server_discovery() 