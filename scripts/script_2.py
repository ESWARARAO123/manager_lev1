# Create systemd service file for the resource manager

systemd_service = '''[Unit]
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
'''

# Create installation script
install_script = '''#!/bin/bash
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
'''

# Create web dashboard example
web_dashboard = '''#!/usr/bin/env python3
"""
Web Dashboard for RHEL Resource Manager
A simple Flask-based web interface
"""

from flask import Flask, jsonify, render_template_string
import json
import sys
import os

# Add the resource manager to path
sys.path.append('/opt/resource_manager')
from rhel_resource_manager import ResourceManager

app = Flask(__name__)
rm = ResourceManager()

# HTML template for the dashboard
HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>RHEL Resource Manager Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5; 
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
        }
        .header { 
            background: #c41e3a; 
            color: white; 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 20px; 
        }
        .metrics-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 20px; 
        }
        .metric-card { 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        .metric-title { 
            font-size: 18px; 
            font-weight: bold; 
            margin-bottom: 10px; 
            color: #333; 
        }
        .metric-value { 
            font-size: 24px; 
            font-weight: bold; 
            color: #c41e3a; 
        }
        .progress-bar { 
            width: 100%; 
            height: 20px; 
            background-color: #e0e0e0; 
            border-radius: 10px; 
            overflow: hidden; 
            margin-top: 10px; 
        }
        .progress-fill { 
            height: 100%; 
            transition: width 0.3s ease; 
        }
        .progress-green { background-color: #4caf50; }
        .progress-yellow { background-color: #ff9800; }
        .progress-red { background-color: #f44336; }
        .process-table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 10px; 
        }
        .process-table th, .process-table td { 
            padding: 8px; 
            text-align: left; 
            border-bottom: 1px solid #ddd; 
        }
        .process-table th { 
            background-color: #f2f2f2; 
        }
        .alerts { 
            background: #fff3cd; 
            border: 1px solid #ffeaa7; 
            border-radius: 8px; 
            padding: 15px; 
            margin-bottom: 20px; 
        }
        .alert-item { 
            padding: 5px 0; 
            border-bottom: 1px solid #ffeaa7; 
        }
        .refresh-btn { 
            background: #c41e3a; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 4px; 
            cursor: pointer; 
            margin-bottom: 20px; 
        }
        .refresh-btn:hover { 
            background: #a01729; 
        }
    </style>
    <script>
        function refreshData() {
            location.reload();
        }
        
        function getProgressColor(value) {
            if (value < 60) return 'progress-green';
            if (value < 80) return 'progress-yellow';
            return 'progress-red';
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖥️ RHEL Resource Manager Dashboard</h1>
            <p>Real-time system monitoring and resource management for Red Hat Enterprise Linux</p>
        </div>
        
        <button class="refresh-btn" onclick="refreshData()">🔄 Refresh</button>
        
        <div id="alerts" class="alerts" style="display: none;">
            <h3>⚠️ Active Alerts</h3>
            <div id="alert-list"></div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">💻 CPU Usage</div>
                <div class="metric-value" id="cpu-value">{{ cpu_percent }}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-progress" 
                         style="width: {{ cpu_percent }}%"></div>
                </div>
                <p>Cores: {{ cpu_count }} | Load Avg: {{ load_avg }}</p>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">🧠 Memory Usage</div>
                <div class="metric-value" id="memory-value">{{ memory_percent }}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="memory-progress" 
                         style="width: {{ memory_percent }}%"></div>
                </div>
                <p>Used: {{ memory_used }} / {{ memory_total }}</p>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">💽 Swap Usage</div>
                <div class="metric-value">{{ swap_percent }}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ swap_percent }}%"></div>
                </div>
                <p>Used: {{ swap_used }} / {{ swap_total }}</p>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">⏱️ System Uptime</div>
                <div class="metric-value">{{ uptime }}</div>
                <p>Last updated: {{ timestamp }}</p>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">🔥 Top CPU Processes</div>
                <table class="process-table">
                    <tr><th>PID</th><th>Name</th><th>CPU%</th><th>User</th></tr>
                    {% for proc in top_cpu %}
                    <tr>
                        <td>{{ proc.pid }}</td>
                        <td>{{ proc.name }}</td>
                        <td>{{ "%.1f"|format(proc.cpu_percent) }}%</td>
                        <td>{{ proc.username }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">🧠 Top Memory Processes</div>
                <table class="process-table">
                    <tr><th>PID</th><th>Name</th><th>Mem%</th><th>User</th></tr>
                    {% for proc in top_memory %}
                    <tr>
                        <td>{{ proc.pid }}</td>
                        <td>{{ proc.name }}</td>
                        <td>{{ "%.1f"|format(proc.memory_percent) }}%</td>
                        <td>{{ proc.username }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
    </div>
    
    <script>
        // Set progress bar colors based on values
        document.getElementById('cpu-progress').className = 
            'progress-fill ' + getProgressColor({{ cpu_percent }});
        document.getElementById('memory-progress').className = 
            'progress-fill ' + getProgressColor({{ memory_percent }});
    </script>
</body>
</html>'''

@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        status = rm.get_system_status()
        metrics = status.get('system_metrics', {})
        
        # Format data for template
        data = {
            'cpu_percent': round(metrics.get('cpu', {}).get('percent', 0), 1),
            'cpu_count': metrics.get('cpu', {}).get('count', 0),
            'load_avg': ', '.join([f"{x:.2f}" for x in metrics.get('cpu', {}).get('load_avg', [0, 0, 0])]),
            'memory_percent': round(metrics.get('memory', {}).get('percent', 0), 1),
            'memory_used': f"{metrics.get('memory', {}).get('used', 0) // (1024**3)} GB",
            'memory_total': f"{metrics.get('memory', {}).get('total', 0) // (1024**3)} GB",
            'swap_percent': round(metrics.get('swap', {}).get('percent', 0), 1),
            'swap_used': f"{metrics.get('swap', {}).get('used', 0) // (1024**3)} GB",
            'swap_total': f"{metrics.get('swap', {}).get('total', 0) // (1024**3)} GB",
            'uptime': f"{int(psutil.boot_time())} seconds",
            'timestamp': metrics.get('timestamp', ''),
            'top_cpu': status.get('top_cpu_processes', [])[:5],
            'top_memory': status.get('top_memory_processes', [])[:5],
        }
        
        return render_template_string(HTML_TEMPLATE, **data)
        
    except Exception as e:
        return f"Error loading dashboard: {e}", 500

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    try:
        status = rm.get_system_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-group/<name>')
def api_create_group(name):
    """API endpoint to create resource group"""
    try:
        cpu_limit = request.args.get('cpu_limit', 512, type=int)
        memory_limit = request.args.get('memory_limit', '1G')
        
        success = rm.create_resource_group(name, cpu_limit, memory_limit)
        return jsonify({'success': success, 'group': name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting RHEL Resource Manager Web Dashboard...")
    print("Access at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
'''

# Save all files
with open('resource-manager.service', 'w') as f:
    f.write(systemd_service)

with open('install.sh', 'w') as f:
    f.write(install_script)

with open('web_dashboard.py', 'w') as f:
    f.write(web_dashboard)

# Make install script executable
os.chmod('install.sh', 0o755)
os.chmod('web_dashboard.py', 0o755)

print("Created additional files:")
print("1. resource-manager.service - systemd service configuration")
print("2. install.sh - automated installation script")
print("3. web_dashboard.py - Flask-based web dashboard")
print("\nInstallation steps:")
print("1. sudo ./install.sh")
print("2. sudo systemctl start resource-manager")
print("3. python3 web_dashboard.py (for web interface)")