#!/usr/bin/env python3.12
"""
Test Remote Server Data Access
Verifies that SSH is working and remote server data is accessible
"""

import subprocess
from datetime import datetime

def test_remote_server_data():
    """Test getting data from remote server"""
    print("🔍 Testing Remote Server Data Access")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test SSH connection
    print("📡 Testing SSH connection...")
    try:
        result = subprocess.run([
            'ssh', 'root@172.16.16.23', 'echo "SSH connection successful"'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ SSH connection successful")
        else:
            print("❌ SSH connection failed")
            return False
    except Exception as e:
        print(f"❌ SSH connection error: {e}")
        return False
    
    # Get CPU usage
    print("\n💻 Getting CPU usage...")
    try:
        cpu_result = subprocess.run([
            'ssh', 'root@172.16.16.23', 
            "top -bn1 | grep 'Cpu(s)' | awk '{print \$2}' | cut -d'%' -f1"
        ], capture_output=True, text=True, timeout=10)
        
        if cpu_result.returncode == 0:
            cpu_usage = float(cpu_result.stdout.strip())
            print(f"✅ CPU Usage: {cpu_usage:.1f}%")
        else:
            print("❌ Failed to get CPU usage")
            return False
    except Exception as e:
        print(f"❌ CPU usage error: {e}")
        return False
    
    # Get memory usage
    print("\n🧠 Getting memory usage...")
    try:
        mem_result = subprocess.run([
            'ssh', 'root@172.16.16.23',
            "free -m | grep '^Mem:' | awk '{print \$3/\$2*100}'"
        ], capture_output=True, text=True, timeout=10)
        
        if mem_result.returncode == 0:
            memory_percent = float(mem_result.stdout.strip())
            print(f"✅ Memory Usage: {memory_percent:.1f}%")
        else:
            print("❌ Failed to get memory usage")
            return False
    except Exception as e:
        print(f"❌ Memory usage error: {e}")
        return False
    
    # Get disk usage
    print("\n💾 Getting disk usage...")
    try:
        disk_result = subprocess.run([
            'ssh', 'root@172.16.16.23',
            "df -h / | tail -1 | awk '{print \$5}' | cut -d'%' -f1"
        ], capture_output=True, text=True, timeout=10)
        
        if disk_result.returncode == 0:
            disk_percent = int(disk_result.stdout.strip())
            print(f"✅ Disk Usage: {disk_percent}%")
        else:
            print("❌ Failed to get disk usage")
            return False
    except Exception as e:
        print(f"❌ Disk usage error: {e}")
        return False
    
    # Get load average
    print("\n📊 Getting load average...")
    try:
        load_result = subprocess.run([
            'ssh', 'root@172.16.16.23',
            "cat /proc/loadavg | awk '{print \$1}'"
        ], capture_output=True, text=True, timeout=10)
        
        if load_result.returncode == 0:
            load_avg = float(load_result.stdout.strip())
            print(f"✅ Load Average: {load_avg:.2f}")
        else:
            print("❌ Failed to get load average")
            return False
    except Exception as e:
        print(f"❌ Load average error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All remote server data tests passed!")
    print("✅ SSH is working correctly")
    print("✅ Remote server data is accessible")
    print("✅ Web dashboard should now show remote server details")
    print("\n💡 You can now:")
    print("   - Use the web dashboard with server switching")
    print("   - See real-time remote server metrics")
    print("   - Monitor both servers simultaneously")
    
    return True

if __name__ == "__main__":
    test_remote_server_data() 