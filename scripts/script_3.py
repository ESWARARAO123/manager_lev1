# Create systemd service file and installation components (fixed)

# Create systemd service file
systemd_service = """[Unit]
Description=RHEL CPU and Memory Resource Manager
Documentation=https://docs.redhat.com/
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
ExecStart=/usr/bin/python3 /opt/resource_manager/rhel_resource_manager.py --monitor --interval 30
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure
RestartSec=42s

# Resource limits for the service itself
CPUShares=100
MemoryLimit=128M

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log /sys/fs/cgroup /opt/resource_manager

# Environment
Environment=PYTHONPATH=/opt/resource_manager
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
Alias=resource-manager.service
"""

# Installation script
install_script = """#!/bin/bash
# Installation script for RHEL Resource Manager

set -e

echo "Installing RHEL CPU and Memory Resource Manager..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Check RHEL version
if ! grep -q "Red Hat Enterprise Linux" /etc/redhat-release 2>/dev/null; then
    echo "Warning: This system may not be RHEL. Continuing anyway..."
fi

# Install Python dependencies
echo "Installing Python dependencies..."
if command -v dnf &> /dev/null; then
    dnf install -y python3 python3-pip python3-devel
else
    yum install -y python3 python3-pip python3-devel
fi

pip3 install psutil

# Create installation directory
echo "Creating installation directory..."
mkdir -p /opt/resource_manager
mkdir -p /var/log/resource_manager

# Copy files
echo "Installing resource manager..."
cp rhel_resource_manager.py /opt/resource_manager/
chmod +x /opt/resource_manager/rhel_resource_manager.py

# Create systemd service
echo "Creating systemd service..."
cp resource-manager.service /etc/systemd/system/

# Enable and start service
echo "Enabling service..."
systemctl daemon-reload
systemctl enable resource-manager.service

# Create logrotate configuration
cat > /etc/logrotate.d/resource-manager << EOF
/var/log/resource_manager.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF

echo "Installation complete!"
echo ""
echo "Usage:"
echo "  Start service:    systemctl start resource-manager"
echo "  Stop service:     systemctl stop resource-manager"
echo "  Check status:     systemctl status resource-manager"
echo "  View logs:        journalctl -u resource-manager -f"
echo "  Manual status:    /opt/resource_manager/rhel_resource_manager.py --status"
echo ""
echo "Configuration files:"
echo "  Service:          /etc/systemd/system/resource-manager.service"
echo "  Script:           /opt/resource_manager/rhel_resource_manager.py"
echo "  Logs:             /var/log/resource_manager.log"
"""

# Simple monitoring configuration file
config_file = """# RHEL Resource Manager Configuration
# Edit this file to customize resource management settings

[monitoring]
# Monitoring interval in seconds
interval = 30

# Alert thresholds (percentage)
cpu_threshold = 80.0
memory_threshold = 80.0

# History size (number of data points to keep)
history_size = 1000

[cgroups]
# Default cgroup settings
default_cpu_shares = 1024
default_memory_limit = 1G

# Enable cgroup management
enable_cgroups = true

[systemd]
# Enable systemd service management
enable_systemd = true

# Default service resource limits
default_service_cpu_shares = 512
default_service_memory_limit = 512M

[logging]
# Log level (DEBUG, INFO, WARNING, ERROR)
log_level = INFO

# Log file location
log_file = /var/log/resource_manager.log

# Enable syslog
enable_syslog = true

[alerts]
# Enable email alerts
enable_email = false
smtp_server = localhost
smtp_port = 587
alert_email = admin@example.com

# Enable syslog alerts
enable_syslog_alerts = true
"""

# Create a simple CLI tool for common operations
cli_tool = """#!/usr/bin/env python3
"""
RHEL Resource Manager CLI Tool
Quick commands for common resource management tasks
"""

import sys
import argparse
import subprocess
import json

class ResourceManagerCLI:
    def __init__(self):
        self.rm_path = "/opt/resource_manager/rhel_resource_manager.py"
    
    def show_status(self):
        """Show system resource status"""
        try:
            result = subprocess.run([sys.executable, self.rm_path, "--status"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                status = json.loads(result.stdout)
                self.print_status(status)
            else:
                print(f"Error: {result.stderr}")
        except Exception as e:
            print(f"Error getting status: {e}")
    
    def print_status(self, status):
        """Print formatted status"""
        metrics = status.get('system_metrics', {})
        
        print("🖥️  RHEL System Resource Status")
        print("=" * 40)
        
        # CPU Info
        cpu = metrics.get('cpu', {})
        print(f"💻 CPU Usage: {cpu.get('percent', 0):.1f}%")
        print(f"   Cores: {cpu.get('count', 0)}")
        load_avg = cpu.get('load_avg', [0, 0, 0])
        print(f"   Load Average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
        
        # Memory Info
        memory = metrics.get('memory', {})
        total_gb = memory.get('total', 0) / (1024**3)
        used_gb = memory.get('used', 0) / (1024**3)
        print(f"🧠 Memory Usage: {memory.get('percent', 0):.1f}%")
        print(f"   Used: {used_gb:.1f}GB / {total_gb:.1f}GB")
        
        # Swap Info
        swap = metrics.get('swap', {})
        print(f"💽 Swap Usage: {swap.get('percent', 0):.1f}%")
        
        # Top Processes
        print("\\n🔥 Top CPU Processes:")
        for i, proc in enumerate(status.get('top_cpu_processes', [])[:3], 1):
            print(f"   {i}. {proc.get('name', 'N/A')} (PID: {proc.get('pid', 'N/A')}) - {proc.get('cpu_percent', 0):.1f}%")
        
        print("\\n🧠 Top Memory Processes:")
        for i, proc in enumerate(status.get('top_memory_processes', [])[:3], 1):
            print(f"   {i}. {proc.get('name', 'N/A')} (PID: {proc.get('pid', 'N/A')}) - {proc.get('memory_percent', 0):.1f}%")
        
        # Recent Alerts
        alerts = status.get('recent_alerts', [])
        if alerts:
            print("\\n⚠️  Recent Alerts:")
            for alert in alerts[-3:]:
                print(f"   {alert.get('message', 'N/A')}")
    
    def create_group(self, name, cpu_limit, memory_limit):
        """Create a resource group"""
        try:
            result = subprocess.run([
                sys.executable, self.rm_path, 
                "--create-group", name,
                "--cpu-limit", str(cpu_limit),
                "--memory-limit", memory_limit
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Successfully created resource group '{name}'")
                print(f"   CPU Limit: {cpu_limit} shares")
                print(f"   Memory Limit: {memory_limit}")
            else:
                print(f"❌ Error creating group: {result.stderr}")
        except Exception as e:
            print(f"Error: {e}")
    
    def monitor(self, interval=30):
        """Start monitoring"""
        print(f"Starting resource monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop...")
        try:
            subprocess.run([sys.executable, self.rm_path, "--monitor", "--interval", str(interval)])
        except KeyboardInterrupt:
            print("\\nMonitoring stopped.")

def main():
    parser = argparse.ArgumentParser(description="RHEL Resource Manager CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Create group command
    create_parser = subparsers.add_parser('create-group', help='Create resource group')
    create_parser.add_argument('name', help='Group name')
    create_parser.add_argument('--cpu', type=int, default=512, help='CPU shares')
    create_parser.add_argument('--memory', default='1G', help='Memory limit')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Start monitoring')
    monitor_parser.add_argument('--interval', type=int, default=30, help='Monitoring interval')
    
    args = parser.parse_args()
    cli = ResourceManagerCLI()
    
    if args.command == 'status':
        cli.show_status()
    elif args.command == 'create-group':
        cli.create_group(args.name, args.cpu, args.memory)
    elif args.command == 'monitor':
        cli.monitor(args.interval)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
"""

# Save all files
with open('resource-manager.service', 'w') as f:
    f.write(systemd_service)

with open('install.sh', 'w') as f:
    f.write(install_script)

with open('resource-manager.conf', 'w') as f:
    f.write(config_file)

with open('rmcli.py', 'w') as f:
    f.write(cli_tool)

# Make scripts executable
import os
os.chmod('install.sh', 0o755)
os.chmod('rmcli.py', 0o755)

print("✅ Created Resource Manager components:")
print("   📄 resource-manager.service - systemd service file")
print("   📄 install.sh - installation script")  
print("   📄 resource-manager.conf - configuration file")
print("   📄 rmcli.py - CLI management tool")
print()
print("📋 Quick Setup Guide:")
print("   1. sudo ./install.sh")
print("   2. sudo systemctl start resource-manager")
print("   3. ./rmcli.py status")
print("   4. ./rmcli.py monitor")
print()
print("🔧 Management Commands:")
print("   ./rmcli.py status")
print("   ./rmcli.py create-group myapp --cpu 512 --memory 1G")
print("   ./rmcli.py monitor --interval 30")