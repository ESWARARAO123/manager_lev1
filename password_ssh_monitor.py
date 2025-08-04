#!/usr/bin/env python3.12
"""
Password-based SSH Monitoring
Monitors remote server using SSH with password authentication
"""

import subprocess
import time
import getpass
from datetime import datetime

class PasswordSSHMonitor:
    def __init__(self):
        self.password = None
        self.ssh_available = False
    
    def setup_password(self):
        """Get SSH password from user"""
        print("🔐 SSH Password Setup")
        print("=" * 30)
        print("To monitor the remote server, we need your SSH password")
        print("This will be stored in memory only (not saved to disk)")
        print()
        
        try:
            self.password = getpass.getpass("Enter SSH password for root@172.16.16.23: ")
            if self.password:
                print("✅ Password stored in memory")
                return True
            else:
                print("❌ No password provided")
                return False
        except Exception as e:
            print(f"❌ Error getting password: {e}")
            return False
    
    def test_ssh_with_password(self):
        """Test SSH connection with password"""
        if not self.password:
            return False
        
        try:
            # Use sshpass to provide password
            result = subprocess.run([
                'sshpass', '-p', self.password,
                'ssh', '-o', 'StrictHostKeyChecking=no',
                'root@172.16.16.23', 'echo "SSH test successful"'
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
        except FileNotFoundError:
            print("❌ sshpass not installed. Installing...")
            try:
                subprocess.run(['sudo', 'yum', 'install', '-y', 'sshpass'], check=True)
                print("✅ sshpass installed")
                return self.test_ssh_with_password()
            except:
                print("❌ Failed to install sshpass")
                return False
        except Exception as e:
            print(f"❌ SSH test failed: {e}")
            return False
    
    def get_remote_server_info(self):
        """Get detailed remote server information"""
        if not self.password:
            return None
        
        try:
            # CPU usage
            cpu_cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
            cpu_result = subprocess.run([
                'sshpass', '-p', self.password,
                'ssh', '-o', 'StrictHostKeyChecking=no',
                'root@172.16.16.23', cpu_cmd
            ], capture_output=True, text=True, timeout=10)
            cpu_usage = float(cpu_result.stdout.strip()) if cpu_result.stdout.strip() else 0.0
            
            # Memory usage
            mem_cmd = "free -m | grep '^Mem:' | awk '{print $2, $3, $4, $3/$2*100}'"
            mem_result = subprocess.run([
                'sshpass', '-p', self.password,
                'ssh', '-o', 'StrictHostKeyChecking=no',
                'root@172.16.16.23', mem_cmd
            ], capture_output=True, text=True, timeout=10)
            
            memory_percent = 0.0
            if mem_result.stdout.strip():
                parts = mem_result.stdout.strip().split()
                memory_percent = float(parts[3]) if len(parts) > 3 else 0.0
            
            # Disk usage
            disk_cmd = "df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1"
            disk_result = subprocess.run([
                'sshpass', '-p', self.password,
                'ssh', '-o', 'StrictHostKeyChecking=no',
                'root@172.16.16.23', disk_cmd
            ], capture_output=True, text=True, timeout=10)
            disk_percent = int(disk_result.stdout.strip()) if disk_result.stdout.strip() else 0
            
            # Load average
            load_cmd = "cat /proc/loadavg | awk '{print $1}'"
            load_result = subprocess.run([
                'sshpass', '-p', self.password,
                'ssh', '-o', 'StrictHostKeyChecking=no',
                'root@172.16.16.23', load_cmd
            ], capture_output=True, text=True, timeout=10)
            load_avg = float(load_result.stdout.strip()) if load_result.stdout.strip() else 0.0
            
            return {
                'name': 'Remote Server',
                'ip': '172.16.16.23',
                'status': 'Online',
                'cpu_percent': cpu_usage,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'load_avg': load_avg,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            return {
                'name': 'Remote Server',
                'ip': '172.16.16.23',
                'status': 'Error',
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    def display_status(self, local_info, remote_info):
        """Display status of both servers"""
        print(f"\n📊 Server Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print(f"{'Server':<20} {'IP':<15} {'CPU %':<8} {'Memory %':<10} {'Disk %':<8} {'Load':<8} {'Status':<10}")
        print("-" * 80)
        
        # Local server
        if local_info and 'error' not in local_info:
            cpu = f"{local_info['cpu_percent']:.1f}"
            memory = f"{local_info['memory_percent']:.1f}"
            disk = f"{local_info['disk_percent']}"
            load = f"{local_info['load_avg']:.2f}"
            
            cpu_color = "🟢" if local_info['cpu_percent'] < 80 else "🟡" if local_info['cpu_percent'] < 90 else "🔴"
            mem_color = "🟢" if local_info['memory_percent'] < 80 else "🟡" if local_info['memory_percent'] < 90 else "🔴"
            
            print(f"{local_info['name']:<20} {local_info['ip']:<15} {cpu_color}{cpu:<7} {mem_color}{memory:<9} {disk:<8} {load:<8} {'✅ Online':<10}")
        else:
            print(f"{'Local Server':<20} {'172.16.16.21':<15} {'ERROR':<8} {'ERROR':<10} {'ERROR':<8} {'ERROR':<8} {'❌ Error':<10}")
        
        # Remote server
        if remote_info and 'error' not in remote_info:
            cpu = f"{remote_info['cpu_percent']:.1f}"
            memory = f"{remote_info['memory_percent']:.1f}"
            disk = f"{remote_info['disk_percent']}"
            load = f"{remote_info['load_avg']:.2f}"
            
            cpu_color = "🟢" if remote_info['cpu_percent'] < 80 else "🟡" if remote_info['cpu_percent'] < 90 else "🔴"
            mem_color = "🟢" if remote_info['memory_percent'] < 80 else "🟡" if remote_info['memory_percent'] < 90 else "🔴"
            
            print(f"{remote_info['name']:<20} {remote_info['ip']:<15} {cpu_color}{cpu:<7} {mem_color}{memory:<9} {disk:<8} {load:<8} {'✅ Online':<10}")
        else:
            status = remote_info.get('status', 'Unknown') if remote_info else 'Unknown'
            print(f"{'Remote Server':<20} {'172.16.16.23':<15} {'N/A':<8} {'N/A':<10} {'N/A':<8} {'N/A':<8} {'❌ ' + status:<10}")
        
        print("-" * 80)
    
    def monitor_servers(self):
        """Monitor both servers continuously"""
        print("🚀 Password-based SSH Monitoring")
        print("=" * 40)
        print("Monitoring both servers with SSH password authentication")
        print()
        
        # Setup password
        if not self.setup_password():
            print("❌ Password setup failed")
            return
        
        # Test SSH connection
        print("\n🔍 Testing SSH connection...")
        if not self.test_ssh_with_password():
            print("❌ SSH connection failed")
            print("💡 Check your password and network connectivity")
            return
        
        print("✅ SSH connection successful!")
        print("\n⏱️  Starting monitoring... (Press Ctrl+C to stop)")
        print("=" * 50)
        
        try:
            while True:
                # Get local server info
                import psutil
                local_info = {
                    'name': 'Local Server',
                    'ip': '172.16.16.21',
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('/').percent,
                    'load_avg': psutil.getloadavg()[0]
                }
                
                # Get remote server info
                remote_info = self.get_remote_server_info()
                
                # Display status
                self.display_status(local_info, remote_info)
                
                # Wait before next update
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():
    """Main function"""
    monitor = PasswordSSHMonitor()
    monitor.monitor_servers()

if __name__ == "__main__":
    main() 