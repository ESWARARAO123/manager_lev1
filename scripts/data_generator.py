#!/usr/bin/env python3.12
"""
Data generation utilities for RHEL Resource Manager
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

class DataGenerator:
    """Generate sample data for testing and demonstration"""
    
    @staticmethod
    def generate_system_resource_data(days: int = 1, interval_minutes: int = 5, 
                                    output_file: str = "system_resource_monitoring_data.csv") -> str:
        """Generate sample system resource monitoring data"""
        # Generate sample data for system resource monitoring
        np.random.seed(42)
        
        # Create timestamps for specified days with specified interval
        start_time = datetime.now() - timedelta(days=days)
        total_intervals = int((days * 24 * 60) / interval_minutes)
        timestamps = [start_time + timedelta(minutes=interval_minutes*i) for i in range(total_intervals)]
        
        # Generate realistic CPU and memory usage patterns
        cpu_usage = []
        memory_usage = []
        
        for i, ts in enumerate(timestamps):
            # Create realistic patterns based on time of day
            hour = ts.hour
            
            # Higher usage during business hours (9-17)
            if 9 <= hour <= 17:
                base_cpu = 45 + np.random.normal(0, 10)
                base_memory = 65 + np.random.normal(0, 8)
            # Lower usage during night (22-6)
            elif hour >= 22 or hour <= 6:
                base_cpu = 15 + np.random.normal(0, 5)
                base_memory = 35 + np.random.normal(0, 5)
            # Moderate usage during other hours
            else:
                base_cpu = 30 + np.random.normal(0, 8)
                base_memory = 50 + np.random.normal(0, 7)
            
            # Add some spikes for realistic behavior
            if np.random.random() < 0.05:  # 5% chance of spike
                base_cpu += np.random.normal(25, 5)
                base_memory += np.random.normal(15, 3)
            
            # Ensure values are within realistic bounds
            cpu_usage.append(max(0, min(100, base_cpu)))
            memory_usage.append(max(0, min(100, base_memory)))
        
        # Create DataFrame
        resource_data = pd.DataFrame({
            'timestamp': timestamps,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage
        })
        
        # Add some derived metrics
        resource_data['cpu_threshold_exceeded'] = resource_data['cpu_usage'] > 80
        resource_data['memory_threshold_exceeded'] = resource_data['memory_usage'] > 80
        resource_data['combined_load'] = (resource_data['cpu_usage'] + resource_data['memory_usage']) / 2
        
        # Save to CSV
        resource_data.to_csv(output_file, index=False)
        
        # Display sample statistics
        print("Sample System Resource Monitoring Data:")
        print(resource_data.head(10))
        print(f"\nTotal data points: {len(resource_data)}")
        print(f"CPU Usage - Mean: {resource_data['cpu_usage'].mean():.1f}%, Max: {resource_data['cpu_usage'].max():.1f}%")
        print(f"Memory Usage - Mean: {resource_data['memory_usage'].mean():.1f}%, Max: {resource_data['memory_usage'].max():.1f}%")
        print(f"Threshold violations - CPU: {resource_data['cpu_threshold_exceeded'].sum()}, Memory: {resource_data['memory_threshold_exceeded'].sum()}")
        print(f"\nData saved to {output_file}")
        
        return output_file
    
    @staticmethod
    def generate_process_data(num_processes: int = 50, output_file: str = "process_data.csv") -> str:
        """Generate sample process data"""
        np.random.seed(42)
        
        # Sample process names
        process_names = [
            'systemd', 'sshd', 'bash', 'python3', 'nginx', 'mysql', 'postgresql',
            'docker', 'kubelet', 'etcd', 'apache2', 'php-fpm', 'redis-server',
            'memcached', 'elasticsearch', 'logstash', 'kibana', 'prometheus',
            'grafana', 'node_exporter', 'cadvisor', 'fluentd', 'filebeat',
            'metricbeat', 'packetbeat', 'heartbeat', 'auditbeat', 'journalbeat'
        ]
        
        # Generate process data
        processes = []
        for i in range(num_processes):
            process = {
                'pid': np.random.randint(1, 65535),
                'name': np.random.choice(process_names),
                'cpu_percent': np.random.exponential(5),
                'memory_percent': np.random.exponential(2),
                'create_time': datetime.now() - timedelta(hours=np.random.randint(1, 168)),
                'username': np.random.choice(['root', 'systemd', 'nginx', 'mysql', 'postgres', 'docker'])
            }
            
            # Ensure percentages are within reasonable bounds
            process['cpu_percent'] = min(100, process['cpu_percent'])
            process['memory_percent'] = min(100, process['memory_percent'])
            
            processes.append(process)
        
        # Create DataFrame
        df = pd.DataFrame(processes)
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        
        print(f"Generated {num_processes} process records")
        print(f"Data saved to {output_file}")
        
        return output_file
    
    @staticmethod
    def generate_alert_data(num_alerts: int = 20, output_file: str = "alert_data.json") -> str:
        """Generate sample alert data"""
        np.random.seed(42)
        
        alert_types = ['cpu_high', 'memory_high', 'disk_full', 'network_down', 'service_down']
        severity_levels = ['low', 'medium', 'high', 'critical']
        
        alerts = []
        for i in range(num_alerts):
            alert_type = np.random.choice(alert_types)
            severity = np.random.choice(severity_levels)
            
            # Generate timestamp within last 24 hours
            timestamp = datetime.now() - timedelta(
                hours=np.random.randint(0, 24),
                minutes=np.random.randint(0, 60)
            )
            
            alert = {
                'id': f"alert_{i+1:04d}",
                'type': alert_type,
                'severity': severity,
                'timestamp': timestamp.isoformat(),
                'message': f"Sample {alert_type} alert with {severity} severity",
                'value': np.random.randint(80, 100) if 'high' in alert_type else np.random.randint(50, 80),
                'threshold': 80 if 'high' in alert_type else 70,
                'resolved': np.random.choice([True, False], p=[0.7, 0.3])
            }
            
            alerts.append(alert)
        
        # Save to JSON
        with open(output_file, 'w') as f:
            json.dump(alerts, f, indent=2, default=str)
        
        print(f"Generated {num_alerts} alert records")
        print(f"Data saved to {output_file}")
        
        return output_file
    
    @staticmethod
    def generate_cgroup_data(num_groups: int = 10, output_file: str = "cgroup_data.json") -> str:
        """Generate sample cgroup data"""
        np.random.seed(42)
        
        group_names = [
            'web_servers', 'database', 'cache', 'monitoring', 'logging',
            'backup', 'development', 'testing', 'production', 'staging'
        ]
        
        cgroups = []
        for i in range(min(num_groups, len(group_names))):
            cgroup = {
                'name': group_names[i],
                'cpu_shares': np.random.choice([256, 512, 1024, 2048]),
                'memory_limit': f"{np.random.randint(1, 16)}G",
                'cpu_usage_ns': np.random.randint(1000000000, 10000000000),
                'memory_usage_bytes': np.random.randint(1024**3, 8 * 1024**3),
                'memory_limit_bytes': np.random.randint(2 * 1024**3, 16 * 1024**3),
                'processes': np.random.randint(1, 20),
                'created': (datetime.now() - timedelta(days=np.random.randint(1, 30))).isoformat()
            }
            
            cgroups.append(cgroup)
        
        # Save to JSON
        with open(output_file, 'w') as f:
            json.dump(cgroups, f, indent=2, default=str)
        
        print(f"Generated {len(cgroups)} cgroup records")
        print(f"Data saved to {output_file}")
        
        return output_file 