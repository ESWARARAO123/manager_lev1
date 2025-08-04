#!/usr/bin/env python3.12
"""
Test Enhanced Server Discovery
Tests the enhanced server discovery with disk and process information
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_server_discovery():
    """Test the enhanced server discovery functionality"""
    print("🧪 Testing Enhanced Server Discovery")
    print("=" * 50)
    
    try:
        from core.server_discovery import ServerDiscovery
        print("✅ Server discovery module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import server discovery module: {e}")
        return False
    
    # Initialize server discovery
    discovery = ServerDiscovery()
    print("✅ Server discovery initialized")
    
    # Test with a known server (replace with your actual server IP)
    test_ip = "172.16.16.23"  # Your remote server
    username = "root"
    
    print(f"\n🔍 Testing enhanced system info for {test_ip}...")
    
    # Test SSH connection first
    ssh_ok = discovery.test_ssh_connection(test_ip, username)
    print(f"SSH connection test: {'✅' if ssh_ok else '❌'}")
    
    if ssh_ok:
        # Test enhanced system info
        print("📊 Fetching enhanced system information...")
        system_info = discovery._get_system_info(test_ip, username)
        
        if system_info and 'error' not in system_info:
            print("✅ Enhanced system info retrieved successfully!")
            print(f"   CPU: {system_info.get('cpu_percent', 0):.1f}%")
            print(f"   Memory: {system_info.get('memory_percent', 0):.1f}%")
            print(f"   Disk: {system_info.get('disk_percent', 0)}%")
            print(f"   Load Average: {system_info.get('load_avg', 0):.2f}")
            
            # Check for disk partitions
            partitions = system_info.get('disk_partitions', [])
            print(f"   Disk Partitions: {len(partitions)} found")
            for i, partition in enumerate(partitions[:3]):  # Show first 3
                print(f"     {i+1}. {partition.get('device', 'Unknown')} -> {partition.get('mountpoint', 'Unknown')} ({partition.get('usage', {}).get('percent', 0)}%)")
            
            # Check for processes
            processes = system_info.get('processes', [])
            print(f"   Top Processes: {len(processes)} found")
            for i, process in enumerate(processes[:5]):  # Show first 5
                print(f"     {i+1}. {process.get('name', 'Unknown')} (PID: {process.get('pid', 0)}) - CPU: {process.get('cpu_percent', 0):.1f}%, MEM: {process.get('memory_percent', 0):.1f}%")
            
            print("\n🎉 Enhanced server discovery test completed successfully!")
            print("💡 The dashboard should now show disk and process information for remote servers.")
            
        else:
            print("❌ Failed to get enhanced system info")
            if 'error' in system_info:
                print(f"   Error: {system_info['error']}")
    else:
        print("💡 SSH connection failed. Make sure:")
        print("   - The server is reachable")
        print("   - SSH key authentication is set up")
        print("   - Or use password authentication in the web interface")
    
    return True

if __name__ == "__main__":
    test_enhanced_server_discovery() 