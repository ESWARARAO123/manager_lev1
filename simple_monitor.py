#!/usr/bin/env python3.12
"""
Simple Multi-Server Monitoring (No sshpass required)
Monitors 172.16.16.21 (local) and 172.16.16.23 (remote)
"""

import subprocess
import time
import psutil
from datetime import datetime
import threading
import queue

class SimpleMonitor:
    def __init__(self):
        self.local_info = {}
        self.remote_info = {}
        self.running = False
        self.update_queue = queue.Queue()
    
    def get_local_info(self):
        """Get local server information"""
        try:
            return {
                'ip': '172.16.16.21',
                'name': 'Local Server',
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_avg': psutil.getloadavg(),
                'uptime': time.time() - psutil.boot_time(),
                'timestamp': datetime.now(),
                'status': 'Online'
            }
        except Exception as e:
            return {
                'ip': '172.16.16.21',
                'name': 'Local Server',
                'error': str(e),
                'timestamp': datetime.now(),
                'status': 'Error'
            }
    
    def test_remote_connection(self):
        """Test if remote server is reachable"""
        try:
            result = subprocess.run(
                ['ssh', '-o', 'ConnectTimeout=5', 'root@172.16.16.23', 'echo "test"'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def display_status(self):
        """Display current status of both servers"""
        print(f"\n📊 Server Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print(f"{'Server':<20} {'IP':<15} {'CPU %':<8} {'Memory %':<10} {'Disk %':<8} {'Load':<8} {'Status':<10}")
        print("-" * 80)
        
        # Display local server
        if self.local_info:
            info = self.local_info
            if 'error' not in info:
                cpu = f"{info['cpu_percent']:.1f}"
                memory = f"{info['memory_percent']:.1f}"
                disk = f"{info['disk_percent']}"
                load = f"{info['load_avg'][0]:.2f}"
                
                cpu_color = "🟢" if info['cpu_percent'] < 80 else "🟡" if info['cpu_percent'] < 90 else "🔴"
                mem_color = "🟢" if info['memory_percent'] < 80 else "🟡" if info['memory_percent'] < 90 else "🔴"
                
                print(f"{info['name']:<20} {info['ip']:<15} {cpu_color}{cpu:<7} {mem_color}{memory:<9} {disk:<8} {load:<8} {'✅ Online':<10}")
            else:
                print(f"{info['name']:<20} {info['ip']:<15} {'ERROR':<8} {'ERROR':<10} {'ERROR':<8} {'ERROR':<8} {'❌ Error':<10}")
        
        # Display remote server
        remote_status = "✅ Online" if self.test_remote_connection() else "❌ Offline"
        print(f"{'Remote Server':<20} {'172.16.16.23':<15} {'N/A':<8} {'N/A':<10} {'N/A':<8} {'N/A':<8} {remote_status:<10}")
        
        print("-" * 80)
        print("💡 For detailed remote monitoring, use: ssh root@172.16.16.23")
    
    def monitor_local(self):
        """Monitor local server continuously"""
        while self.running:
            try:
                self.local_info = self.get_local_info()
                time.sleep(30)
            except Exception as e:
                print(f"Error monitoring local server: {e}")
                time.sleep(30)
    
    def start_monitoring(self):
        """Start monitoring both servers"""
        print("🚀 Simple Multi-Server Monitoring")
        print("=" * 50)
        print("Monitoring: 172.16.16.21 (Local) and 172.16.16.23 (Remote)")
        print("💡 Remote server requires manual SSH connection")
        print()
        
        self.running = True
        
        # Start local monitoring in background thread
        local_thread = threading.Thread(target=self.monitor_local, daemon=True)
        local_thread.start()
        
        try:
            while True:
                self.display_status()
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            self.running = False

def main():
    """Main function"""
    monitor = SimpleMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main() 