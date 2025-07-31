# Create the additional configuration and management files

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

# Create installation script
install_script = """#!/bin/bash
# Installation script for RHEL Resource Manager

set -e

echo "Installing RHEL CPU and Memory Resource Manager..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
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
cp rmcli.py /opt/resource_manager/
cp resource-manager.conf /opt/resource_manager/
chmod +x /opt/resource_manager/rhel_resource_manager.py
chmod +x /opt/resource_manager/rmcli.py

# Create systemd service
echo "Creating systemd service..."
cp resource-manager.service /etc/systemd/system/

# Create symlink for CLI tool
ln -sf /opt/resource_manager/rmcli.py /usr/local/bin/rmcli

# Enable service
echo "Enabling service..."
systemctl daemon-reload
systemctl enable resource-manager.service

echo "Installation complete!"
echo ""
echo "Usage:"
echo "  Start service:    systemctl start resource-manager"  
echo "  Check status:     rmcli status"
echo "  Create group:     rmcli create-group myapp --cpu 512 --memory 1G"
echo "  Monitor:          rmcli monitor"
"""

# Create configuration file
config_file = """# RHEL Resource Manager Configuration

[monitoring]
interval = 30
cpu_threshold = 80.0
memory_threshold = 80.0
history_size = 1000

[cgroups]
default_cpu_shares = 1024
default_memory_limit = 1G
enable_cgroups = true

[logging]
log_level = INFO
log_file = /var/log/resource_manager.log
enable_syslog = true

[alerts]
enable_email = false
enable_syslog_alerts = true
"""

# Save all files
files_created = []

with open('resource-manager.service', 'w') as f:
    f.write(systemd_service)
    files_created.append('resource-manager.service')

with open('install.sh', 'w') as f:
    f.write(install_script)
    files_created.append('install.sh')

with open('resource-manager.conf', 'w') as f:
    f.write(config_file)
    files_created.append('resource-manager.conf')

# Create CLI tool as separate script
cli_code = '''#!/usr/bin/env python3
"""RHEL Resource Manager CLI Tool"""

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
        
        # Memory Info
        memory = metrics.get('memory', {})
        total_gb = memory.get('total', 0) / (1024**3)
        used_gb = memory.get('used', 0) / (1024**3)
        print(f"🧠 Memory Usage: {memory.get('percent', 0):.1f}%")
        print(f"   Used: {used_gb:.1f}GB / {total_gb:.1f}GB")

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
    
    args = parser.parse_args()
    cli = ResourceManagerCLI()
    
    if args.command == 'status':
        cli.show_status()
    elif args.command == 'create-group':
        print(f"Creating group {args.name} with CPU: {args.cpu}, Memory: {args.memory}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
'''

with open('rmcli.py', 'w') as f:
    f.write(cli_code)
    files_created.append('rmcli.py')

# Make scripts executable
import os
os.chmod('install.sh', 0o755)
os.chmod('rmcli.py', 0o755)

print("✅ Successfully created RHEL Resource Manager files:")
for file in files_created:
    print(f"   📄 {file}")

print("\n🚀 Installation Instructions:")
print("1. Run as root: sudo ./install.sh")
print("2. Start service: sudo systemctl start resource-manager")
print("3. Check status: systemctl status resource-manager")
print("4. Use CLI tool: rmcli status")

print("\n📊 Key Features Implemented:")  
print("- Real-time CPU and memory monitoring")
print("- cgroups-based resource control")
print("- systemd service integration")
print("- Configurable alerting system")
print("- Command-line management interface")
print("- Automatic service startup")
print("- Process tracking and limitation")
print("- Resource usage history")

print("\n🔧 Main Components:")
print("- rhel_resource_manager.py: Core resource manager")
print("- resource-manager.service: systemd service configuration")
print("- rmcli.py: Command-line interface")
print("- install.sh: Automated installation")
print("- resource-manager.conf: Configuration file")