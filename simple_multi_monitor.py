#!/usr/bin/env python3.12
"""
Simple Multi-Server Monitoring
Monitors 172.16.16.21 (local) and 172.16.16.23 (remote) with password authentication
"""

import subprocess
import time
import json
import psutil
from datetime import datetime
import getpass

def get_local_system_info():
    """Get system information for local server"""
    try:
        return {
            'ip': '172.16.16.21',
            'name': 'Local Server',
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'load_avg': psutil.getloadavg(),
            'uptime': time.time() - psutil.boot_time(),
            'timestamp': datetime.now()
        }
    except Exception as e:
        return {
            'ip': '172.16.16.21',
            'name': 'Local Server',
            'error': str(e),
            'timestamp': datetime.now()
        }

def get_remote_system_info(ip, password):
    """Get system information for remote server via SSH"""
    try:
        # Create SSH command with password
        ssh_cmd = f'sshpass -p "{password}" ssh -o StrictHostKeyChecking=no root@{ip}'
        
        # Get CPU usage
        cpu_cmd = f'{ssh_cmd} "top -bn1 | grep \\"Cpu(s)\\" | awk \\"{{print \\$2}}\\" | cut -d\\"%\\" -f1"'
        cpu_result = subprocess.run(cpu_cmd, shell=True, capture_output=True, text=True, timeout=10)
        cpu_usage = float(cpu_result.stdout.strip()) if cpu_result.stdout.strip() else 0.0
        
        # Get memory usage
        mem_cmd = f'{ssh_cmd} "free -m | grep \\"^Mem:\\" | awk \\"{{print \\$3/\\$2*100}}\\""'
        mem_result = subprocess.run(mem_cmd, shell=True, capture_output=True, text=True, timeout=10)
        memory_percent = float(mem_result.stdout.strip()) if mem_result.stdout.strip() else 0.0
        
        # Get disk usage
        disk_cmd = f'{ssh_cmd} "df -h / | tail -1 | awk \\"{{print \\$5}}\\" | cut -d\\"%\\" -f1"'
        disk_result = subprocess.run(disk_cmd, shell=True, capture_output=True, text=True, timeout=10)
        disk_percent = int(disk_result.stdout.strip()) if disk_result.stdout.strip() else 0
        
        # Get load average
        load_cmd = f'{ssh_cmd} "cat /proc/loadavg | awk \\"{{print \\$1}}\\""'
        load_result = subprocess.run(load_cmd, shell=True, capture_output=True, text=True, timeout=10)
        load_avg = float(load_result.stdout.strip()) if load_result.stdout.strip() else 0.0
        
        return {
            'ip': ip,
            'name': 'Remote Server',
            'cpu_percent': cpu_usage,
            'memory_percent': memory_percent,
            'disk_percent': disk_percent,
            'load_avg': [load_avg, 0.0, 0.0],
            'uptime': 0,
            'timestamp': datetime.now()
        }
        
    except Exception as e:
        return {
            'ip': ip,
            'name': 'Remote Server',
            'error': str(e),
            'timestamp': datetime.now()
        }

def display_status(servers_info):
    """Display current server status"""
    print(f"\n📊 Server Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"{'Server':<20} {'IP':<15} {'CPU %':<8} {'Memory %':<10} {'Disk %':<8} {'Load':<8} {'Status':<10}")
    print("-" * 80)
    
    for info in servers_info:
        if 'error' in info:
            print(f"{info['name']:<20} {info['ip']:<15} {'ERROR':<8} {'ERROR':<10} {'ERROR':<8} {'ERROR':<8} {'❌ Error':<10}")
        else:
            cpu = f"{info['cpu_percent']:.1f}"
            memory = f"{info['memory_percent']:.1f}"
            disk = f"{info['disk_percent']}"
            load = f"{info['load_avg'][0]:.2f}"
            
            # Color coding based on usage
            cpu_color = "🟢" if info['cpu_percent'] < 80 else "🟡" if info['cpu_percent'] < 90 else "🔴"
            mem_color = "🟢" if info['memory_percent'] < 80 else "🟡" if info['memory_percent'] < 90 else "🔴"
            
            print(f"{info['name']:<20} {info['ip']:<15} {cpu_color}{cpu:<7} {mem_color}{memory:<9} {disk:<8} {load:<8} {'✅ Online':<10}")
    
    print("-" * 80)

def main():
    """Main monitoring function"""
    print("🚀 Simple Multi-Server Monitoring")
    print("=" * 50)
    print("Monitoring: 172.16.16.21 (Local) and 172.16.16.23 (Remote)")
    print()
    
    # Check if sshpass is available
    try:
        subprocess.run(['sshpass', '-V'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ sshpass is not installed. Installing...")
        try:
            subprocess.run(['sudo', 'yum', 'install', '-y', 'sshpass'], check=True)
            print("✅ sshpass installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install sshpass. Please install it manually:")
            print("   sudo yum install -y sshpass")
            return
    
    # Get password for remote server
    print("🔐 Enter password for remote server (172.16.16.23):")
    password = getpass.getpass()
    
    print(f"\n⏱️  Starting monitoring... (Press Ctrl+C to stop)")
    print("=" * 50)
    
    try:
        while True:
            # Get local server info
            local_info = get_local_system_info()
            
            # Get remote server info
            remote_info = get_remote_system_info('172.16.16.23', password)
            
            # Display status
            display_status([local_info, remote_info])
            
            # Wait before next update
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 