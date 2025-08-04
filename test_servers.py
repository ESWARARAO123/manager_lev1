#!/usr/bin/env python3.12
"""
Test script for server connectivity
Tests connection to 172.16.16.21 and 172.16.16.23
"""

import sys
import os
import subprocess
import time
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ping(ip):
    """Test ping connectivity to a server"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', ip],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def test_ssh(ip, username="root"):
    """Test SSH connectivity to a server"""
    try:
        # Test SSH connection with timeout
        result = subprocess.run(
            ['ssh', '-o', 'ConnectTimeout=5', '-o', 'BatchMode=yes', f'{username}@{ip}', 'echo "SSH test successful"'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

def get_local_system_info():
    """Get system information for local server"""
    try:
        import psutil
        
        info = {
            'hostname': psutil.gethostname(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory()._asdict(),
            'disk': psutil.disk_usage('/')._asdict(),
            'load_avg': psutil.getloadavg(),
            'uptime': time.time() - psutil.boot_time()
        }
        return info
    except Exception as e:
        return {'error': str(e)}

def get_remote_system_info(ip, username="root"):
    """Get system information for remote server via SSH"""
    try:
        # Get CPU usage
        cpu_cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
        cpu_result = subprocess.run(
            ['ssh', f'{username}@{ip}', cpu_cmd],
            capture_output=True,
            text=True,
            timeout=10
        )
        cpu_usage = float(cpu_result.stdout.strip()) if cpu_result.stdout.strip() else 0.0
        
        # Get memory usage
        mem_cmd = "free -m | grep '^Mem:' | awk '{print $2, $3, $4, $3/$2*100}'"
        mem_result = subprocess.run(
            ['ssh', f'{username}@{ip}', mem_cmd],
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
        
        # Get disk usage
        disk_cmd = "df -h / | tail -1 | awk '{print $2, $3, $4, $5}'"
        disk_result = subprocess.run(
            ['ssh', f'{username}@{ip}', disk_cmd],
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
        
        # Get load average
        load_cmd = "cat /proc/loadavg | awk '{print $1, $2, $3}'"
        load_result = subprocess.run(
            ['ssh', f'{username}@{ip}', load_cmd],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        load_avg = [0.0, 0.0, 0.0]
        if load_result.stdout.strip():
            parts = load_result.stdout.strip().split()
            load_avg = [float(parts[0]), float(parts[1]), float(parts[2])]
        
        # Get uptime
        uptime_cmd = "uptime -p"
        uptime_result = subprocess.run(
            ['ssh', f'{username}@{ip}', uptime_cmd],
            capture_output=True,
            text=True,
            timeout=10
        )
        uptime = uptime_result.stdout.strip() if uptime_result.stdout.strip() else "Unknown"
        
        return {
            'cpu_percent': cpu_usage,
            'memory': memory_info,
            'disk': disk_info,
            'load_average': load_avg,
            'uptime': uptime
        }
        
    except Exception as e:
        return {'error': str(e)}

def main():
    """Main test function"""
    print("🔍 Testing Server Connectivity")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    servers = {
        "172.16.16.21": "Local Server",
        "172.16.16.23": "Remote Server"
    }
    
    results = {}
    
    for ip, name in servers.items():
        print(f"📡 Testing {name} ({ip})...")
        
        # Test ping
        ping_ok = test_ping(ip)
        print(f"   Ping: {'✅' if ping_ok else '❌'}")
        
        # Test SSH
        ssh_ok = test_ssh(ip)
        print(f"   SSH: {'✅' if ssh_ok else '❌'}")
        
        results[ip] = {
            'name': name,
            'ping': ping_ok,
            'ssh': ssh_ok,
            'info': None
        }
        
        # Get system information if SSH is available
        if ssh_ok:
            print(f"   📊 Getting system information...")
            if ip == "172.16.16.21":
                info = get_local_system_info()
            else:
                info = get_remote_system_info(ip)
            
            results[ip]['info'] = info
            
            if 'error' not in info:
                print(f"   ✅ System info retrieved successfully")
            else:
                print(f"   ❌ Error getting system info: {info['error']}")
        
        print()
    
    # Display results
    print("📊 Test Results Summary")
    print("=" * 50)
    
    for ip, result in results.items():
        print(f"\n🏠 {result['name']} ({ip})")
        print(f"   Ping: {'✅' if result['ping'] else '❌'}")
        print(f"   SSH: {'✅' if result['ssh'] else '❌'}")
        
        if result['info'] and 'error' not in result['info']:
            info = result['info']
            print(f"   📈 System Status:")
            
            if 'cpu_percent' in info:
                print(f"      CPU: {info['cpu_percent']:.1f}%")
            
            if 'memory' in info and 'percent' in info['memory']:
                print(f"      Memory: {info['memory']['percent']:.1f}%")
            
            if 'disk' in info and 'percent' in info['disk']:
                print(f"      Disk: {info['disk']['percent']}%")
            
            if 'load_average' in info:
                load = info['load_average']
                print(f"      Load: {load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}")
            
            if 'uptime' in info:
                print(f"      Uptime: {info['uptime']}")
        elif result['info'] and 'error' in result['info']:
            print(f"   ❌ Error: {result['info']['error']}")
    
    print("\n" + "=" * 50)
    
    # Summary
    accessible_servers = [ip for ip, result in results.items() if result['ssh']]
    print(f"✅ Accessible servers: {len(accessible_servers)}")
    for ip in accessible_servers:
        print(f"   - {ip} ({results[ip]['name']})")
    
    if len(accessible_servers) > 0:
        print(f"\n🚀 Ready for multi-server monitoring!")
        print(f"Use: python3 main.py --multi-server-gui")
        print(f"Or: python3 utils/network_cli.py monitor")

if __name__ == "__main__":
    main() 