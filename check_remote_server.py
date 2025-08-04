#!/usr/bin/env python3.12
"""
Manual Remote Server Check
Check detailed status of 172.16.16.23 when needed
"""

import subprocess
import time
from datetime import datetime

def check_remote_server():
    """Check detailed status of remote server"""
    print("🔍 Checking Remote Server (172.16.16.23)")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test connectivity
    print("📡 Testing connectivity...")
    try:
        ping_result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', '172.16.16.23'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if ping_result.returncode == 0:
            print("✅ Ping: Successful")
        else:
            print("❌ Ping: Failed")
            return
    except Exception as e:
        print(f"❌ Ping: Error - {e}")
        return
    
    # Test SSH connectivity
    print("\n🔐 Testing SSH connectivity...")
    try:
        ssh_result = subprocess.run(
            ['ssh', '-o', 'ConnectTimeout=5', 'root@172.16.16.23', 'echo "SSH test successful"'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if ssh_result.returncode == 0:
            print("✅ SSH: Successful")
        else:
            print("❌ SSH: Failed - Password required or connection refused")
            print("💡 Try: ssh root@172.16.16.23")
            return
    except Exception as e:
        print(f"❌ SSH: Error - {e}")
        return
    
    # Get system information
    print("\n📊 Getting system information...")
    try:
        # CPU usage
        cpu_cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
        cpu_result = subprocess.run(
            ['ssh', 'root@172.16.16.23', cpu_cmd],
            capture_output=True,
            text=True,
            timeout=10
        )
        cpu_usage = float(cpu_result.stdout.strip()) if cpu_result.stdout.strip() else 0.0
        
        # Memory usage
        mem_cmd = "free -m | grep '^Mem:' | awk '{print $2, $3, $4, $3/$2*100}'"
        mem_result = subprocess.run(
            ['ssh', 'root@172.16.16.23', mem_cmd],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        memory_info = {}
        if mem_result.stdout.strip():
            parts = mem_result.stdout.strip().split()
            memory_info = {
                'total_mb': int(parts[0]),
                'used_mb': int(parts[1]),
                'free_mb': int(parts[2]),
                'percent': float(parts[3])
            }
        
        # Disk usage
        disk_cmd = "df -h / | tail -1 | awk '{print $2, $3, $4, $5}'"
        disk_result = subprocess.run(
            ['ssh', 'root@172.16.16.23', disk_cmd],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        disk_info = {}
        if disk_result.stdout.strip():
            parts = disk_result.stdout.strip().split()
            disk_info = {
                'total': parts[0],
                'used': parts[1],
                'available': parts[2],
                'percent': int(parts[3].rstrip('%'))
            }
        
        # Load average
        load_cmd = "cat /proc/loadavg | awk '{print $1, $2, $3}'"
        load_result = subprocess.run(
            ['ssh', 'root@172.16.16.23', load_cmd],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        load_avg = [0.0, 0.0, 0.0]
        if load_result.stdout.strip():
            parts = load_result.stdout.strip().split()
            load_avg = [float(parts[0]), float(parts[1]), float(parts[2])]
        
        # Uptime
        uptime_cmd = "uptime -p"
        uptime_result = subprocess.run(
            ['ssh', 'root@172.16.16.23', uptime_cmd],
            capture_output=True,
            text=True,
            timeout=10
        )
        uptime = uptime_result.stdout.strip() if uptime_result.stdout.strip() else "Unknown"
        
        # Display results
        print("\n📈 Remote Server Status:")
        print("=" * 30)
        print(f"CPU Usage: {cpu_usage:.1f}%")
        
        if memory_info:
            print(f"Memory Usage: {memory_info['percent']:.1f}% ({memory_info['used_mb']}/{memory_info['total_mb']} MB)")
        
        if disk_info:
            print(f"Disk Usage: {disk_info['percent']}% ({disk_info['used']}/{disk_info['total']})")
        
        print(f"Load Average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
        print(f"Uptime: {uptime}")
        
        # Status summary
        print("\n📊 Status Summary:")
        cpu_status = "🟢" if cpu_usage < 80 else "🟡" if cpu_usage < 90 else "🔴"
        mem_status = "🟢" if memory_info.get('percent', 0) < 80 else "🟡" if memory_info.get('percent', 0) < 90 else "🔴"
        disk_status = "🟢" if disk_info.get('percent', 0) < 80 else "🟡" if disk_info.get('percent', 0) < 90 else "🔴"
        
        print(f"CPU: {cpu_status} {cpu_usage:.1f}%")
        print(f"Memory: {mem_status} {memory_info.get('percent', 0):.1f}%")
        print(f"Disk: {disk_status} {disk_info.get('percent', 0)}%")
        
    except Exception as e:
        print(f"❌ Error getting system information: {e}")

def main():
    """Main function"""
    print("🚀 Remote Server Check Tool")
    print("=" * 40)
    print("This tool will check the status of 172.16.16.23")
    print("You may be prompted for SSH password")
    print()
    
    try:
        check_remote_server()
    except KeyboardInterrupt:
        print("\n👋 Check cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 