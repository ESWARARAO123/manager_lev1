#!/usr/bin/env python3.12
"""
RHEL Resource Manager Headless GUI Application
Console-based interface for monitoring CPU and Memory resources
Works without X11 display environment
"""

import psutil
import time
import json
import threading
import sys
import os
from datetime import datetime, timedelta
from collections import deque
import numpy as np

class HeadlessResourceManager:
    def __init__(self):
        self.cpu_data = deque(maxlen=100)
        self.memory_data = deque(maxlen=100)
        self.timestamps = deque(maxlen=100)
        self.monitoring = False
        self.monitor_thread = None
        
    def clear_screen(self):
        """Clear the console screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_header(self):
        """Print application header"""
        print("=" * 80)
        print("🖥️  RHEL Resource Manager - Headless Console Interface")
        print("=" * 80)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
    def get_system_info(self):
        """Get system information"""
        try:
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'CPU Cores': cpu_count,
                'CPU Frequency': f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A",
                'Total Memory': f"{memory.total / (1024**3):.1f} GB",
                'Available Memory': f"{memory.available / (1024**3):.1f} GB",
                'Total Disk': f"{disk.total / (1024**3):.1f} GB",
                'Free Disk': f"{disk.free / (1024**3):.1f} GB",
                'System Load': f"{psutil.getloadavg()[0]:.2f}"
            }
        except Exception as e:
            return {'Error': str(e)}
            
    def get_current_metrics(self):
        """Get current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            now = datetime.now()
            self.timestamps.append(now)
            self.cpu_data.append(cpu_percent)
            self.memory_data.append(memory.percent)
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'memory_total_gb': memory.total / (1024**3),
                'memory_available_gb': memory.available / (1024**3)
            }
        except Exception as e:
            return {'error': str(e)}
            
    def print_dashboard(self):
        """Print dashboard view"""
        self.clear_screen()
        self.print_header()
        
        # Get current metrics
        metrics = self.get_current_metrics()
        system_info = self.get_system_info()
        
        print("\n📊 SYSTEM DASHBOARD")
        print("-" * 50)
        
        # CPU Information
        print(f"💻 CPU Usage: {metrics['cpu_percent']:6.1f}%")
        print(f"   Cores: {system_info['CPU Cores']}")
        print(f"   Frequency: {system_info['CPU Frequency']}")
        print(f"   Load Average: {system_info['System Load']}")
        
        # Memory Information
        print(f"\n🧠 Memory Usage: {metrics['memory_percent']:6.1f}%")
        print(f"   Used: {metrics['memory_used_gb']:6.1f} GB")
        print(f"   Available: {metrics['memory_available_gb']:6.1f} GB")
        print(f"   Total: {metrics['memory_total_gb']:6.1f} GB")
        
        # Disk Information
        print(f"\n💾 Disk Usage:")
        print(f"   Free: {system_info['Free Disk']}")
        print(f"   Total: {system_info['Total Disk']}")
        
        # Status indicators
        print(f"\n🔍 STATUS INDICATORS:")
        cpu_status = "🟢 Normal" if metrics['cpu_percent'] < 80 else "🟡 Warning" if metrics['cpu_percent'] < 90 else "🔴 Critical"
        mem_status = "🟢 Normal" if metrics['memory_percent'] < 80 else "🟡 Warning" if metrics['memory_percent'] < 90 else "🔴 Critical"
        
        print(f"   CPU: {cpu_status}")
        print(f"   Memory: {mem_status}")
        
        # Recent history (last 10 points)
        if len(self.cpu_data) > 1:
            print(f"\n📈 RECENT HISTORY (Last 10 measurements):")
            print("-" * 50)
            print("Time                CPU%    Memory%")
            print("-" * 50)
            
            for i in range(max(0, len(self.timestamps) - 10), len(self.timestamps)):
                time_str = self.timestamps[i].strftime('%H:%M:%S')
                cpu_val = self.cpu_data[i]
                mem_val = self.memory_data[i]
                print(f"{time_str}          {cpu_val:6.1f}%  {mem_val:6.1f}%")
        
        print("\n" + "=" * 80)
        
    def print_cpu_details(self):
        """Print detailed CPU information"""
        self.clear_screen()
        self.print_header()
        
        metrics = self.get_current_metrics()
        
        print("\n💻 CPU DETAILED ANALYSIS")
        print("-" * 50)
        
        # Current CPU info
        print(f"Current CPU Usage: {metrics['cpu_percent']:6.1f}%")
        
        # CPU statistics
        if len(self.cpu_data) > 0:
            cpu_list = list(self.cpu_data)
            print(f"Average CPU Usage: {np.mean(cpu_list):6.1f}%")
            print(f"Maximum CPU Usage: {np.max(cpu_list):6.1f}%")
            print(f"Minimum CPU Usage: {np.min(cpu_list):6.1f}%")
            
            # CPU trend
            if len(cpu_list) >= 2:
                trend = "↗️ Increasing" if cpu_list[-1] > cpu_list[-2] else "↘️ Decreasing" if cpu_list[-1] < cpu_list[-2] else "➡️ Stable"
                print(f"CPU Trend: {trend}")
        
        # CPU cores info
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        print(f"CPU Cores: {cpu_count}")
        print(f"CPU Frequency: {cpu_freq.current:.0f} MHz" if cpu_freq else "CPU Frequency: N/A")
        
        # Load average
        load_avg = psutil.getloadavg()
        print(f"Load Average (1/5/15 min): {load_avg[0]:.2f} / {load_avg[1]:.2f} / {load_avg[2]:.2f}")
        
        # CPU usage by core (if available)
        try:
            cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
            print(f"\n📊 CPU Usage by Core:")
            for i, usage in enumerate(cpu_per_core):
                status = "🟢" if usage < 50 else "🟡" if usage < 80 else "🔴"
                print(f"   Core {i+1}: {usage:6.1f}% {status}")
        except:
            pass
        
        # Top CPU processes
        print(f"\n🔥 TOP CPU PROCESSES:")
        print("-" * 50)
        print("PID     CPU%   Memory%  Name")
        print("-" * 50)
        
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            
            for proc in processes[:10]:
                pid = proc.get('pid', 'N/A')
                cpu = proc.get('cpu_percent', 0)
                memory = proc.get('memory_percent', 0)
                name = proc.get('name', 'Unknown')[:20]
                print(f"{pid:6d}  {cpu:6.1f}%  {memory:6.1f}%  {name}")
                
        except Exception as e:
            print(f"Error getting process info: {e}")
        
        print("\n" + "=" * 80)
        
    def print_memory_details(self):
        """Print detailed memory information"""
        self.clear_screen()
        self.print_header()
        
        metrics = self.get_current_metrics()
        memory = psutil.virtual_memory()
        
        print("\n🧠 MEMORY DETAILED ANALYSIS")
        print("-" * 50)
        
        # Current memory info
        print(f"Current Memory Usage: {metrics['memory_percent']:6.1f}%")
        print(f"Used Memory: {metrics['memory_used_gb']:6.1f} GB")
        print(f"Available Memory: {metrics['memory_available_gb']:6.1f} GB")
        print(f"Total Memory: {metrics['memory_total_gb']:6.1f} GB")
        
        # Memory statistics
        if len(self.memory_data) > 0:
            mem_list = list(self.memory_data)
            print(f"Average Memory Usage: {np.mean(mem_list):6.1f}%")
            print(f"Maximum Memory Usage: {np.max(mem_list):6.1f}%")
            print(f"Minimum Memory Usage: {np.min(mem_list):6.1f}%")
            
            # Memory trend
            if len(mem_list) >= 2:
                trend = "↗️ Increasing" if mem_list[-1] > mem_list[-2] else "↘️ Decreasing" if mem_list[-1] < mem_list[-2] else "➡️ Stable"
                print(f"Memory Trend: {trend}")
        
        # Memory breakdown
        print(f"\n📊 MEMORY BREAKDOWN:")
        print("-" * 30)
        print(f"Total:      {memory.total / (1024**3):8.1f} GB")
        print(f"Used:       {memory.used / (1024**3):8.1f} GB")
        print(f"Available:  {memory.available / (1024**3):8.1f} GB")
        print(f"Free:       {memory.free / (1024**3):8.1f} GB")
        print(f"Buffers:    {memory.buffers / (1024**3):8.1f} GB")
        print(f"Cached:     {memory.cached / (1024**3):8.1f} GB")
        
        # Swap information
        try:
            swap = psutil.swap_memory()
            print(f"\n💾 SWAP MEMORY:")
            print("-" * 30)
            print(f"Total Swap: {swap.total / (1024**3):8.1f} GB")
            print(f"Used Swap:  {swap.used / (1024**3):8.1f} GB")
            print(f"Free Swap:  {swap.free / (1024**3):8.1f} GB")
            print(f"Swap Usage: {swap.percent:8.1f}%")
        except:
            print("\n💾 SWAP MEMORY: Not available")
        
        # Top memory processes
        print(f"\n🔥 TOP MEMORY PROCESSES:")
        print("-" * 50)
        print("PID     CPU%   Memory%  Name")
        print("-" * 50)
        
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by memory usage
            processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
            
            for proc in processes[:10]:
                pid = proc.get('pid', 'N/A')
                cpu = proc.get('cpu_percent', 0)
                memory = proc.get('memory_percent', 0)
                name = proc.get('name', 'Unknown')[:20]
                print(f"{pid:6d}  {cpu:6.1f}%  {memory:6.1f}%  {name}")
                
        except Exception as e:
            print(f"Error getting process info: {e}")
        
        print("\n" + "=" * 80)
        
    def start_monitoring(self):
        """Start continuous monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("✅ Real-time monitoring started!")
        
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring = False
        print("⏹️ Real-time monitoring stopped!")
        
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            time.sleep(5)  # Update every 5 seconds
            
    def show_menu(self):
        """Show main menu"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print("\n📋 MAIN MENU")
            print("-" * 30)
            print("1. 📊 Dashboard View")
            print("2. 💻 CPU Monitor")
            print("3. 🧠 Memory Monitor")
            print("4. ▶️ Start Real-time Monitoring")
            print("5. ⏹️ Stop Real-time Monitoring")
            print("6. 📈 Export Data")
            print("7. ❌ Exit")
            print("-" * 30)
            
            choice = input("\nSelect an option (1-7): ").strip()
            
            if choice == '1':
                self.print_dashboard()
                input("\nPress Enter to continue...")
            elif choice == '2':
                self.print_cpu_details()
                input("\nPress Enter to continue...")
            elif choice == '3':
                self.print_memory_details()
                input("\nPress Enter to continue...")
            elif choice == '4':
                self.start_monitoring()
                input("\nPress Enter to continue...")
            elif choice == '5':
                self.stop_monitoring()
                input("\nPress Enter to continue...")
            elif choice == '6':
                self.export_data()
                input("\nPress Enter to continue...")
            elif choice == '7':
                print("\n👋 Thank you for using RHEL Resource Manager!")
                break
            else:
                print("\n❌ Invalid option. Please try again.")
                time.sleep(2)
                
    def export_data(self):
        """Export monitoring data to JSON"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'cpu_data': list(self.cpu_data),
                'memory_data': list(self.memory_data),
                'timestamps': [ts.isoformat() for ts in self.timestamps],
                'current_metrics': self.get_current_metrics(),
                'system_info': self.get_system_info()
            }
            
            filename = f"resource_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"\n✅ Data exported to {filename}")
            
        except Exception as e:
            print(f"\n❌ Error exporting data: {e}")

def main():
    """Main function"""
    print("🚀 Starting RHEL Resource Manager (Headless Mode)...")
    
    try:
        manager = HeadlessResourceManager()
        manager.show_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 