#!/usr/bin/env python3.12
"""
Test Server Discovery Module
Tests the server discovery and connection functionality
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_server_discovery():
    """Test the server discovery module"""
    print("🧪 Testing Server Discovery Module")
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
    
    # Test status summary
    status = discovery.get_status_summary()
    print(f"📊 Status: {status}")
    
    # Test configuration save/load
    print("\n💾 Testing configuration save/load...")
    save_success = discovery.save_configuration('test_config.json')
    print(f"Save: {'✅' if save_success else '❌'}")
    
    load_success = discovery.load_configuration('test_config.json')
    print(f"Load: {'✅' if load_success else '❌'}")
    
    # Test network scanning (small range for testing)
    print("\n🔍 Testing network scanning...")
    print("Scanning 172.16.16.0/24 (small range for testing)")
    
    discovered = discovery.scan_network('172.16.16.0/24')
    print(f"✅ Scan completed. Found {len(discovered)} servers:")
    
    for ip, info in discovered.items():
        print(f"   📡 {ip} - {info.get('status', 'Unknown')}")
    
    # Test SSH connection to a known server (if available)
    test_ip = "172.16.16.23"  # Your remote server
    if test_ip in discovered:
        print(f"\n🔗 Testing SSH connection to {test_ip}...")
        
        # Test without password (key-based auth)
        ssh_test = discovery.test_ssh_connection(test_ip)
        print(f"SSH test (key auth): {'✅' if ssh_test else '❌'}")
        
        if ssh_test:
            print("✅ SSH connection successful with key authentication")
        else:
            print("💡 SSH connection failed. You can try with password in the web interface.")
    
    print("\n🎉 Server discovery test completed!")
    print("💡 You can now use the web dashboard with the settings button to:")
    print("   - Scan for servers in your network")
    print("   - Connect to servers via SSH")
    print("   - Monitor multiple servers simultaneously")
    
    return True

if __name__ == "__main__":
    test_server_discovery() 