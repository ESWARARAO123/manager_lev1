#!/usr/bin/env python3.12
"""
Quick Status Check - No SSH Prompts
Shows status of both servers without any interactive prompts
"""

import subprocess
import psutil
import time
from datetime import datetime

def get_local_status():
    """Get local server status"""
    try:
        from utils.network_utils import get_local_ip, get_hostname
        
        local_ip = get_local_ip()
        hostname = get_hostname()
        
        return {
            'name': f'Local Server ({hostname})',
            'ip': local_ip,
            'status': 'Online',
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'load_avg': psutil.getloadavg()[0]
        }
    except Exception as e:
        from utils.network_utils import get_local_ip, get_hostname
        local_ip = get_local_ip()
        hostname = get_hostname()
        
        return {
            'name': f'Local Server ({hostname})',
            'ip': local_ip,
            'status': 'Error',
            'error': str(e)
        }

def get_remote_status():
    """Get remote server status using ping only"""
    # This function is now deprecated since we use dynamic discovery
    # Return a placeholder that indicates no remote server is configured
    return {
        'name': 'Remote Server',
        'ip': 'Not configured',
        'status': 'Not configured',
        'note': 'Use server discovery to find and connect to remote servers'
    }

def display_status():
    """Display current status of both servers"""
    print(f"\n📊 Quick Server Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"{'Server':<20} {'IP':<15} {'CPU %':<8} {'Memory %':<10} {'Disk %':<8} {'Load':<8} {'Status':<10}")
    print("-" * 80)
    
    # Local server
    local = get_local_status()
    if local['status'] == 'Online':
        cpu = f"{local['cpu_percent']:.1f}"
        memory = f"{local['memory_percent']:.1f}"
        disk = f"{local['disk_percent']}"
        load = f"{local['load_avg']:.2f}"
        
        cpu_color = "🟢" if local['cpu_percent'] < 80 else "🟡" if local['cpu_percent'] < 90 else "🔴"
        mem_color = "🟢" if local['memory_percent'] < 80 else "🟡" if local['memory_percent'] < 90 else "🔴"
        
        print(f"{local['name']:<20} {local['ip']:<15} {cpu_color}{cpu:<7} {mem_color}{memory:<9} {disk:<8} {load:<8} {'✅ Online':<10}")
    else:
        print(f"{local['name']:<20} {local['ip']:<15} {'ERROR':<8} {'ERROR':<10} {'ERROR':<8} {'ERROR':<8} {'❌ Error':<10}")
    
    # Remote server
    remote = get_remote_status()
    status_color = "🟢" if remote['status'] == 'Online' else "🔴"
    status_text = "✅ Online" if remote['status'] == 'Online' else "❌ Offline"
    print(f"{remote['name']:<20} {remote['ip']:<15} {'N/A':<8} {'N/A':<10} {'N/A':<8} {'N/A':<8} {status_text:<10}")
    
    print("-" * 80)
    print("💡 For detailed remote monitoring: Use the web dashboard with server discovery")

def main():
    """Main function"""
    print("🚀 Quick Server Status Check")
    print("=" * 40)
    print("No SSH prompts - ping only")
    print()
    
    try:
        while True:
            display_status()
            print("\n⏱️  Refreshing in 30 seconds... (Press Ctrl+C to stop)")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n👋 Status check stopped")

if __name__ == "__main__":
    main() 