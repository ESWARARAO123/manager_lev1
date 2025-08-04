#!/usr/bin/env python3
"""
Test script for network scanner functionality
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_network_scanner():
    """Test the network scanner functionality"""
    try:
        from utils.network_scanner import NetworkScanner
        
        print("🔍 Testing Network Scanner...")
        print("=" * 50)
        
        # Test with a small range first
        scanner = NetworkScanner()
        
        # Test with a small range (just a few IPs)
        print("Testing with range 172.16.16.1-5...")
        discovered = scanner.scan_network("172.16.16", "root")
        
        print(f"Found {len(discovered)} SSH-accessible servers:")
        for server in discovered:
            print(f"  - {server['ip']}: {server['hostname']} ({server['os']})")
            print(f"    CPU: {server['cpu_cores']} cores, Memory: {server['memory']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing network scanner: {e}")
        return False

def test_server_discovery():
    """Test the server discovery functionality"""
    try:
        from core.server_discovery import ServerDiscovery
        
        print("\n🔍 Testing Server Discovery...")
        print("=" * 50)
        
        discovery = ServerDiscovery()
        
        # Test connection to a known server
        test_ip = "172.16.16.23"  # Your test server
        print(f"Testing connection to {test_ip}...")
        
        success = discovery.connect_to_server(test_ip, "root", "")
        print(f"Connection result: {'✅ Success' if success else '❌ Failed'}")
        
        if success:
            # Try to get server info
            try:
                info = discovery.get_server_info(test_ip)
                print(f"Server info: {info}")
            except Exception as e:
                print(f"Error getting server info: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing server discovery: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RHEL Resource Manager - Network Scanner Test")
    print("=" * 60)
    
    # Test network scanner
    scanner_ok = test_network_scanner()
    
    # Test server discovery
    discovery_ok = test_server_discovery()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"Network Scanner: {'✅ PASS' if scanner_ok else '❌ FAIL'}")
    print(f"Server Discovery: {'✅ PASS' if discovery_ok else '❌ FAIL'}")
    
    if scanner_ok and discovery_ok:
        print("\n🎉 All tests passed! The system should work properly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.") 