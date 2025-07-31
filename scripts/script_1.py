# Create a comprehensive RHEL CPU and Memory Resource Manager
# This script demonstrates the core functionality

resource_manager_code = '''#!/usr/bin/env python3
"""
RHEL CPU and Memory Resource Manager
A comprehensive system resource management tool for Red Hat Enterprise Linux

Author: System Administrator
Date: 2025
License: MIT
"""

import os
import sys
import time
import json
import psutil
import logging
import subprocess
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/resource_manager.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('ResourceManager')

class SystemMonitor:
    """System monitoring and data collection"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.cpu_history = deque(maxlen=history_size)
        self.memory_history = deque(maxlen=history_size)
        self.process_data = {}
        
    def collect_system_metrics(self) -> Dict:
        """Collect current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            load_avg = os.getloadavg()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk I/O metrics
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network_io = psutil.net_io_counters()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': cpu_freq._asdict() if cpu_freq else None,
                    'load_avg': load_avg
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent,
                    'free': memory.free,
                    'buffers': memory.buffers,
                    'cached': memory.cached
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent
                },
                'disk_io': disk_io._asdict() if disk_io else None,
                'network_io': network_io._asdict() if network_io else None
            }
            
            # Store in history
            self.cpu_history.append((datetime.now(), cpu_percent))
            self.memory_history.append((datetime.now(), memory.percent))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def get_top_processes(self, sort_by: str = 'cpu', limit: int = 10) -> List[Dict]:
        """Get top processes by CPU or memory usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by specified metric
            key = 'cpu_percent' if sort_by == 'cpu' else 'memory_percent'
            processes.sort(key=lambda x: x.get(key, 0), reverse=True)
            
            return processes[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top processes: {e}")
            return []

class CgroupManager:
    """Manage cgroups for resource control"""
    
    def __init__(self):
        self.cgroup_root = "/sys/fs/cgroup"
        self.custom_groups = {}
        
    def create_cgroup(self, name: str, cpu_limit: Optional[int] = None, 
                     memory_limit: Optional[str] = None) -> bool:
        """Create a new cgroup with specified limits"""
        try:
            # Create cgroup directories
            cpu_path = f"{self.cgroup_root}/cpu/{name}"
            memory_path = f"{self.cgroup_root}/memory/{name}"
            
            os.makedirs(cpu_path, exist_ok=True)
            os.makedirs(memory_path, exist_ok=True)
            
            # Set CPU limit (CPU shares)
            if cpu_limit:
                with open(f"{cpu_path}/cpu.shares", 'w') as f:
                    f.write(str(cpu_limit))
            
            # Set memory limit
            if memory_limit:
                with open(f"{memory_path}/memory.limit_in_bytes", 'w') as f:
                    f.write(memory_limit)
                    
                # Disable swap for this cgroup
                with open(f"{memory_path}/memory.swappiness", 'w') as f:
                    f.write("0")
            
            self.custom_groups[name] = {
                'cpu_path': cpu_path,
                'memory_path': memory_path,
                'cpu_limit': cpu_limit,
                'memory_limit': memory_limit
            }
            
            logger.info(f"Created cgroup '{name}' with CPU: {cpu_limit}, Memory: {memory_limit}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating cgroup '{name}': {e}")
            return False
    
    def add_process_to_cgroup(self, cgroup_name: str, pid: int) -> bool:
        """Add a process to a cgroup"""
        try:
            if cgroup_name not in self.custom_groups:
                logger.error(f"Cgroup '{cgroup_name}' does not exist")
                return False
            
            group = self.custom_groups[cgroup_name]
            
            # Add to CPU cgroup
            with open(f"{group['cpu_path']}/cgroup.procs", 'w') as f:
                f.write(str(pid))
            
            # Add to memory cgroup
            with open(f"{group['memory_path']}/cgroup.procs", 'w') as f:
                f.write(str(pid))
            
            logger.info(f"Added process {pid} to cgroup '{cgroup_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error adding process {pid} to cgroup '{cgroup_name}': {e}")
            return False
    
    def get_cgroup_stats(self, cgroup_name: str) -> Dict:
        """Get statistics for a cgroup"""
        try:
            if cgroup_name not in self.custom_groups:
                return {}
            
            group = self.custom_groups[cgroup_name]
            stats = {}
            
            # CPU stats
            try:
                with open(f"{group['cpu_path']}/cpuacct.usage", 'r') as f:
                    stats['cpu_usage_ns'] = int(f.read().strip())
            except:
                stats['cpu_usage_ns'] = 0
            
            # Memory stats
            try:
                with open(f"{group['memory_path']}/memory.usage_in_bytes", 'r') as f:
                    stats['memory_usage_bytes'] = int(f.read().strip())
            except:
                stats['memory_usage_bytes'] = 0
            
            try:
                with open(f"{group['memory_path']}/memory.limit_in_bytes", 'r') as f:
                    stats['memory_limit_bytes'] = int(f.read().strip())
            except:
                stats['memory_limit_bytes'] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cgroup stats for '{cgroup_name}': {e}")
            return {}

class SystemdManager:
    """Manage systemd services and resource control"""
    
    def set_service_resources(self, service_name: str, cpu_shares: Optional[int] = None,
                            memory_limit: Optional[str] = None) -> bool:
        """Set resource limits for a systemd service"""
        try:
            commands = []
            
            if cpu_shares:
                commands.append(f"systemctl set-property {service_name} CPUShares={cpu_shares}")
            
            if memory_limit:
                commands.append(f"systemctl set-property {service_name} MemoryLimit={memory_limit}")
            
            for cmd in commands:
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Failed to execute: {cmd}")
                    logger.error(f"Error: {result.stderr}")
                    return False
            
            logger.info(f"Set resource limits for service '{service_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error setting service resources: {e}")
            return False
    
    def get_service_status(self, service_name: str) -> Dict:
        """Get status of a systemd service"""
        try:
            result = subprocess.run(
                ['systemctl', 'show', service_name, '--property=MainPID,CPUShares,MemoryLimit,ActiveState'],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                return {}
            
            status = {}
            for line in result.stdout.strip().split('\\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    status[key] = value
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {}

class AlertManager:
    """Handle alerting for resource thresholds"""
    
    def __init__(self, cpu_threshold: float = 80.0, memory_threshold: float = 80.0):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.alert_history = deque(maxlen=100)
        
    def check_thresholds(self, metrics: Dict) -> List[Dict]:
        """Check if metrics exceed thresholds and generate alerts"""
        alerts = []
        
        # Check CPU threshold
        if metrics.get('cpu', {}).get('percent', 0) > self.cpu_threshold:
            alert = {
                'type': 'cpu_high',
                'timestamp': datetime.now().isoformat(),
                'value': metrics['cpu']['percent'],
                'threshold': self.cpu_threshold,
                'message': f"High CPU usage: {metrics['cpu']['percent']:.1f}%"
            }
            alerts.append(alert)
            self.alert_history.append(alert)
        
        # Check memory threshold
        if metrics.get('memory', {}).get('percent', 0) > self.memory_threshold:
            alert = {
                'type': 'memory_high',
                'timestamp': datetime.now().isoformat(),
                'value': metrics['memory']['percent'],
                'threshold': self.memory_threshold,
                'message': f"High memory usage: {metrics['memory']['percent']:.1f}%"
            }
            alerts.append(alert)
            self.alert_history.append(alert)
        
        return alerts
    
    def send_alert(self, alert: Dict):
        """Send alert notification"""
        # This could be extended to send emails, SMS, or other notifications
        logger.warning(f"ALERT: {alert['message']}")
        
        # Log to syslog
        os.system(f"logger -t ResourceManager 'ALERT: {alert['message']}'")

class ResourceManager:
    """Main resource manager class"""
    
    def __init__(self):
        self.monitor = SystemMonitor()
        self.cgroup_manager = CgroupManager()
        self.systemd_manager = SystemdManager()
        self.alert_manager = AlertManager()
        self.running = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: int = 60):
        """Start continuous system monitoring"""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("Started resource monitoring")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Stopped resource monitoring")
    
    def _monitor_loop(self, interval: int):
        """Main monitoring loop"""
        while self.running:
            try:
                # Collect metrics
                metrics = self.monitor.collect_system_metrics()
                
                if metrics:
                    # Check for alerts
                    alerts = self.alert_manager.check_thresholds(metrics)
                    
                    # Send alerts
                    for alert in alerts:
                        self.alert_manager.send_alert(alert)
                    
                    # Log metrics
                    logger.info(f"CPU: {metrics['cpu']['percent']:.1f}%, "
                              f"Memory: {metrics['memory']['percent']:.1f}%")
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def create_resource_group(self, name: str, cpu_limit: int, memory_limit: str) -> bool:
        """Create a new resource group with limits"""
        return self.cgroup_manager.create_cgroup(name, cpu_limit, memory_limit)
    
    def assign_process_to_group(self, group_name: str, pid: int) -> bool:
        """Assign a process to a resource group"""
        return self.cgroup_manager.add_process_to_cgroup(group_name, pid)
    
    def set_service_limits(self, service_name: str, cpu_shares: int, memory_limit: str) -> bool:
        """Set resource limits for a systemd service"""
        return self.systemd_manager.set_service_resources(service_name, cpu_shares, memory_limit)
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        metrics = self.monitor.collect_system_metrics()
        top_cpu_processes = self.monitor.get_top_processes('cpu', 5)
        top_memory_processes = self.monitor.get_top_processes('memory', 5)
        
        return {
            'system_metrics': metrics,
            'top_cpu_processes': top_cpu_processes,
            'top_memory_processes': top_memory_processes,
            'recent_alerts': list(self.alert_manager.alert_history)[-10:],
            'cgroups': list(self.cgroup_manager.custom_groups.keys())
        }

def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RHEL CPU and Memory Resource Manager')
    parser.add_argument('--monitor', action='store_true', help='Start monitoring mode')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--create-group', type=str, help='Create resource group')
    parser.add_argument('--cpu-limit', type=int, help='CPU limit (shares)')
    parser.add_argument('--memory-limit', type=str, help='Memory limit (e.g., 1G)')
    
    args = parser.parse_args()
    
    # Initialize resource manager
    rm = ResourceManager()
    
    try:
        if args.status:
            status = rm.get_system_status()
            print(json.dumps(status, indent=2, default=str))
        
        elif args.create_group:
            if args.cpu_limit and args.memory_limit:
                success = rm.create_resource_group(args.create_group, args.cpu_limit, args.memory_limit)
                print(f"Resource group creation: {'Success' if success else 'Failed'}")
            else:
                print("Error: --cpu-limit and --memory-limit required for creating groups")
        
        elif args.monitor:
            print(f"Starting monitoring with {args.interval}s interval...")
            rm.start_monitoring(args.interval)
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\\nStopping monitoring...")
                rm.stop_monitoring()
        
        else:
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

# Save the resource manager script
with open('rhel_resource_manager.py', 'w') as f:
    f.write(resource_manager_code)

print("Created comprehensive RHEL Resource Manager script: rhel_resource_manager.py")
print("\nKey Features:")
print("- System monitoring with psutil")
print("- cgroups management")
print("- systemd service resource control")
print("- Real-time alerting")
print("- CLI interface")
print("- Logging and history tracking")
print("\nUsage examples:")
print("python3 rhel_resource_manager.py --status")
print("python3 rhel_resource_manager.py --monitor --interval 30")
print("python3 rhel_resource_manager.py --create-group myapp --cpu-limit 512 --memory-limit 1G")