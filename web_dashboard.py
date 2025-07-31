#!/usr/bin/env python3.12
"""
Web-based Dashboard for RHEL Resource Manager
Automated dashboard that updates every 5 seconds
"""

import os
import sys
import time
import json
import threading
import webbrowser
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import psutil
import subprocess

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from scripts.real_time_charts import RealTimeCharts
    from scripts.chart_generator import ChartGenerator
except ImportError:
    try:
        from scripts.real_time_charts import RealTimeCharts
        from scripts.chart_generator import ChartGenerator
    except ImportError:
        print("Warning: Chart modules not found. Some features may not work.")

class DashboardData:
    """Manages dashboard data and updates"""
    
    def __init__(self):
        self.charts = RealTimeCharts()
        self.data = {}
        self.update_interval = 5  # seconds
        self.running = False
        self.update_thread = None
        
    def start_monitoring(self):
        """Start continuous monitoring"""
        self.running = True
        self.update_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.update_thread.start()
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            self.update_data()
            time.sleep(self.update_interval)
    
    def update_data(self):
        """Update all dashboard data"""
        try:
            # System information
            self.data['timestamp'] = datetime.now().isoformat()
            self.data['system_info'] = self._get_system_info()
            self.data['resource_usage'] = self._get_resource_usage()
            self.data['processes'] = self._get_top_processes()
            self.data['network_info'] = self._get_network_info()
            self.data['disk_info'] = self._get_disk_info()
            self.data['alerts'] = self._get_alerts()
            
            # Update charts data
            self.charts.update_data()
            
        except Exception as e:
            print(f"Error updating data: {e}")
    
    def _get_system_info(self):
        """Get basic system information"""
        try:
            return {
                'hostname': psutil.gethostname(),
                'platform': psutil.sys.platform,
                'cpu_count': psutil.cpu_count(),
                'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                'uptime': str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())),
                'load_avg': psutil.getloadavg()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_resource_usage(self):
        """Get current resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used': memory.used,
                'memory_total': memory.total,
                'memory_available': memory.available,
                'swap_percent': psutil.swap_memory().percent if hasattr(psutil, 'swap_memory') else 0
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_top_processes(self):
        """Get top processes by resource usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage and get top 10
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:10]
        except Exception as e:
            return []
    
    def _get_network_info(self):
        """Get network information"""
        try:
            net_io = psutil.net_io_counters()
            net_if = psutil.net_if_addrs()
            
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'interfaces': list(net_if.keys())
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_disk_info(self):
        """Get disk information"""
        try:
            disk_usage = psutil.disk_usage('/')
            disk_partitions = psutil.disk_partitions()
            
            return {
                'root_usage': {
                    'total': disk_usage.total,
                    'used': disk_usage.used,
                    'free': disk_usage.free,
                    'percent': disk_usage.percent
                },
                'partitions': [
                    {
                        'device': p.device,
                        'mountpoint': p.mountpoint,
                        'fstype': p.fstype,
                        'usage': psutil.disk_usage(p.mountpoint)._asdict() if os.path.exists(p.mountpoint) else {}
                    }
                    for p in disk_partitions[:5]  # Limit to 5 partitions
                ]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_alerts(self):
        """Get system alerts"""
        alerts = []
        try:
            # CPU alert
            if self.data.get('resource_usage', {}).get('cpu_percent', 0) > 80:
                alerts.append({
                    'type': 'warning',
                    'message': f"High CPU usage: {self.data['resource_usage']['cpu_percent']:.1f}%",
                    'timestamp': datetime.now().isoformat()
                })
            
            # Memory alert
            if self.data.get('resource_usage', {}).get('memory_percent', 0) > 80:
                alerts.append({
                    'type': 'warning',
                    'message': f"High memory usage: {self.data['resource_usage']['memory_percent']:.1f}%",
                    'timestamp': datetime.now().isoformat()
                })
            
            # Disk alert
            if self.data.get('disk_info', {}).get('root_usage', {}).get('percent', 0) > 80:
                alerts.append({
                    'type': 'warning',
                    'message': f"High disk usage: {self.data['disk_info']['root_usage']['percent']:.1f}%",
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            alerts.append({
                'type': 'error',
                'message': f"Error checking alerts: {e}",
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts

class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the dashboard"""
    
    def __init__(self, *args, dashboard_data=None, **kwargs):
        self.dashboard_data = dashboard_data
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self.send_dashboard_page()
        elif path == '/api/data':
            self.send_json_data()
        elif path == '/api/charts':
            self.send_chart_data()
        elif path.startswith('/static/'):
            self.send_static_file(path[8:])  # Remove '/static/' prefix
        else:
            self.send_error(404, "Not Found")
    
    def send_dashboard_page(self):
        """Send the main dashboard HTML page"""
        html = self._get_dashboard_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_json_data(self):
        """Send JSON data for AJAX requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        data = self.dashboard_data.data if self.dashboard_data else {}
        self.wfile.write(json.dumps(data, default=str).encode('utf-8'))
    
    def send_chart_data(self):
        """Send chart data"""
        try:
            if self.dashboard_data and self.dashboard_data.charts:
                # Create a simple chart data
                chart_data = {
                    'cpu_data': list(self.dashboard_data.charts.cpu_data),
                    'memory_data': list(self.dashboard_data.charts.memory_data),
                    'timestamps': [str(ts) for ts in self.dashboard_data.charts.timestamps]
                }
            else:
                chart_data = {'error': 'No chart data available'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(chart_data, default=str).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def send_static_file(self, filename):
        """Send static files (CSS, JS, images)"""
        try:
            if filename == 'style.css':
                content = self._get_css()
                content_type = 'text/css'
            elif filename == 'script.js':
                content = self._get_javascript()
                content_type = 'application/javascript'
            else:
                self.send_error(404, "File not found")
                return
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def _get_dashboard_html(self):
        """Generate the main dashboard HTML"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RHEL Resource Manager - Live Dashboard</title>
    <link rel="stylesheet" href="/static/style.css">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div class="dashboard">
        <header class="dashboard-header">
            <h1>🚀 RHEL Resource Manager - Live Dashboard</h1>
            <div class="header-info">
                <span id="last-update">Last Update: Loading...</span>
                <span id="status" class="status-indicator">🟢 Online</span>
            </div>
        </header>
        
        <div class="dashboard-content">
            <!-- Quick Stats -->
            <div class="stats-grid">
                <div class="stat-card" id="cpu-card">
                    <h3>CPU Usage</h3>
                    <div class="stat-value" id="cpu-value">--</div>
                    <div class="stat-bar">
                        <div class="stat-bar-fill" id="cpu-bar"></div>
                    </div>
                </div>
                
                <div class="stat-card" id="memory-card">
                    <h3>Memory Usage</h3>
                    <div class="stat-value" id="memory-value">--</div>
                    <div class="stat-bar">
                        <div class="stat-bar-fill" id="memory-bar"></div>
                    </div>
                </div>
                
                <div class="stat-card" id="disk-card">
                    <h3>Disk Usage</h3>
                    <div class="stat-value" id="disk-value">--</div>
                    <div class="stat-bar">
                        <div class="stat-bar-fill" id="disk-bar"></div>
                    </div>
                </div>
                
                <div class="stat-card" id="process-card">
                    <h3>Active Processes</h3>
                    <div class="stat-value" id="process-value">--</div>
                    <div class="stat-subtitle">Running</div>
                </div>
            </div>
            
            <!-- Charts Section -->
            <div class="charts-section">
                <div class="chart-container">
                    <h3>Resource Usage Over Time</h3>
                    <div id="resource-chart"></div>
                </div>
            </div>
            
            <!-- System Information -->
            <div class="info-grid">
                <div class="info-card">
                    <h3>System Information</h3>
                    <div id="system-info"></div>
                </div>
                
                <div class="info-card">
                    <h3>Top Processes</h3>
                    <div id="process-list"></div>
                </div>
                
                <div class="info-card">
                    <h3>Network Information</h3>
                    <div id="network-info"></div>
                </div>
                
                <div class="info-card">
                    <h3>Alerts</h3>
                    <div id="alerts-list"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="/static/script.js"></script>
</body>
</html>
"""
    
    def _get_css(self):
        """Generate CSS styles"""
        return """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
}

.dashboard {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

.dashboard-header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.dashboard-header h1 {
    color: #2c3e50;
    font-size: 2rem;
    font-weight: 700;
}

.header-info {
    display: flex;
    gap: 20px;
    align-items: center;
}

.status-indicator {
    font-size: 1.2rem;
    font-weight: bold;
}

.dashboard-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}

.stat-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
}

.stat-card h3 {
    color: #2c3e50;
    margin-bottom: 15px;
    font-size: 1.1rem;
}

.stat-value {
    font-size: 2.5rem;
    font-weight: bold;
    color: #3498db;
    margin-bottom: 10px;
}

.stat-subtitle {
    font-size: 0.9rem;
    color: #7f8c8d;
}

.stat-bar {
    width: 100%;
    height: 8px;
    background: #ecf0f1;
    border-radius: 4px;
    overflow: hidden;
}

.stat-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #2ecc71, #f39c12, #e74c3c);
    transition: width 0.5s ease;
    border-radius: 4px;
}

.charts-section {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.chart-container h3 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 1.3rem;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
}

.info-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.info-card h3 {
    color: #2c3e50;
    margin-bottom: 15px;
    font-size: 1.2rem;
}

.info-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #ecf0f1;
}

.info-item:last-child {
    border-bottom: none;
}

.info-label {
    font-weight: 500;
    color: #34495e;
}

.info-value {
    color: #7f8c8d;
    font-family: 'Courier New', monospace;
}

.process-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #ecf0f1;
}

.process-name {
    font-weight: 500;
    color: #2c3e50;
}

.process-stats {
    display: flex;
    gap: 15px;
    font-size: 0.9rem;
}

.alert-item {
    padding: 10px;
    margin: 5px 0;
    border-radius: 8px;
    border-left: 4px solid;
}

.alert-warning {
    background: #fff3cd;
    border-color: #ffc107;
    color: #856404;
}

.alert-error {
    background: #f8d7da;
    border-color: #dc3545;
    color: #721c24;
}

@media (max-width: 768px) {
    .dashboard-header {
        flex-direction: column;
        gap: 15px;
        text-align: center;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .info-grid {
        grid-template-columns: 1fr;
    }
}
"""
    
    def _get_javascript(self):
        """Generate JavaScript for dashboard functionality"""
        return """
// Dashboard JavaScript
let updateInterval = 5000; // 5 seconds
let chartData = {
    cpu: [],
    memory: [],
    timestamps: []
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    updateDashboard();
    setInterval(updateDashboard, updateInterval);
    initializeChart();
});

async function updateDashboard() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        
        if (data.error) {
            console.error('Error fetching data:', data.error);
            return;
        }
        
        updateStats(data);
        updateSystemInfo(data);
        updateProcessList(data);
        updateNetworkInfo(data);
        updateAlerts(data);
        updateChart(data);
        
        // Update timestamp
        document.getElementById('last-update').textContent = 
            'Last Update: ' + new Date().toLocaleTimeString();
        
    } catch (error) {
        console.error('Error updating dashboard:', error);
        document.getElementById('status').textContent = '🔴 Offline';
        document.getElementById('status').className = 'status-indicator error';
    }
}

function updateStats(data) {
    const resourceUsage = data.resource_usage || {};
    const diskInfo = data.disk_info || {};
    
    // CPU
    const cpuPercent = resourceUsage.cpu_percent || 0;
    document.getElementById('cpu-value').textContent = cpuPercent.toFixed(1) + '%';
    document.getElementById('cpu-bar').style.width = cpuPercent + '%';
    
    // Memory
    const memoryPercent = resourceUsage.memory_percent || 0;
    document.getElementById('memory-value').textContent = memoryPercent.toFixed(1) + '%';
    document.getElementById('memory-bar').style.width = memoryPercent + '%';
    
    // Disk
    const diskPercent = diskInfo.root_usage?.percent || 0;
    document.getElementById('disk-value').textContent = diskPercent.toFixed(1) + '%';
    document.getElementById('disk-bar').style.width = diskPercent + '%';
    
    // Processes
    const processCount = data.processes?.length || 0;
    document.getElementById('process-value').textContent = processCount;
    
    // Update colors based on usage
    updateStatColors('cpu', cpuPercent);
    updateStatColors('memory', memoryPercent);
    updateStatColors('disk', diskPercent);
}

function updateStatColors(type, percent) {
    const card = document.getElementById(type + '-card');
    const value = document.getElementById(type + '-value');
    
    if (percent >= 90) {
        card.style.borderLeft = '4px solid #e74c3c';
        value.style.color = '#e74c3c';
    } else if (percent >= 70) {
        card.style.borderLeft = '4px solid #f39c12';
        value.style.color = '#f39c12';
    } else {
        card.style.borderLeft = '4px solid #2ecc71';
        value.style.color = '#3498db';
    }
}

function updateSystemInfo(data) {
    const systemInfo = data.system_info || {};
    const container = document.getElementById('system-info');
    
    const info = [
        ['Hostname', systemInfo.hostname || 'N/A'],
        ['Platform', systemInfo.platform || 'N/A'],
        ['CPU Cores', systemInfo.cpu_count || 'N/A'],
        ['Uptime', systemInfo.uptime || 'N/A'],
        ['Load Average', systemInfo.load_avg ? systemInfo.load_avg.join(', ') : 'N/A']
    ];
    
    container.innerHTML = info.map(([label, value]) => 
        `<div class="info-item">
            <span class="info-label">${label}:</span>
            <span class="info-value">${value}</span>
        </div>`
    ).join('');
}

function updateProcessList(data) {
    const processes = data.processes || [];
    const container = document.getElementById('process-list');
    
    container.innerHTML = processes.map(proc => 
        `<div class="process-item">
            <div class="process-name">${proc.name || 'Unknown'}</div>
            <div class="process-stats">
                <span>CPU: ${proc.cpu_percent?.toFixed(1) || 0}%</span>
                <span>MEM: ${proc.memory_percent?.toFixed(1) || 0}%</span>
            </div>
        </div>`
    ).join('');
}

function updateNetworkInfo(data) {
    const networkInfo = data.network_info || {};
    const container = document.getElementById('network-info');
    
    const bytesSent = formatBytes(networkInfo.bytes_sent || 0);
    const bytesRecv = formatBytes(networkInfo.bytes_recv || 0);
    
    container.innerHTML = `
        <div class="info-item">
            <span class="info-label">Bytes Sent:</span>
            <span class="info-value">${bytesSent}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Bytes Received:</span>
            <span class="info-value">${bytesRecv}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Interfaces:</span>
            <span class="info-value">${networkInfo.interfaces?.length || 0}</span>
        </div>
    `;
}

function updateAlerts(data) {
    const alerts = data.alerts || [];
    const container = document.getElementById('alerts-list');
    
    if (alerts.length === 0) {
        container.innerHTML = '<div class="info-item">No alerts</div>';
        return;
    }
    
    container.innerHTML = alerts.map(alert => 
        `<div class="alert-item alert-${alert.type}">
            <strong>${alert.type.toUpperCase()}:</strong> ${alert.message}
        </div>`
    ).join('');
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function initializeChart() {
    const layout = {
        title: 'Resource Usage Over Time',
        xaxis: { title: 'Time' },
        yaxis: { title: 'Usage %', range: [0, 100] },
        height: 400,
        margin: { t: 50, b: 50, l: 50, r: 50 }
    };
    
    Plotly.newPlot('resource-chart', [], layout);
}

function updateChart(data) {
    const resourceUsage = data.resource_usage || {};
    const timestamp = new Date();
    
    // Add new data points
    chartData.cpu.push(resourceUsage.cpu_percent || 0);
    chartData.memory.push(resourceUsage.memory_percent || 0);
    chartData.timestamps.push(timestamp);
    
    // Keep only last 20 points
    if (chartData.cpu.length > 20) {
        chartData.cpu.shift();
        chartData.memory.shift();
        chartData.timestamps.shift();
    }
    
    const traces = [
        {
            x: chartData.timestamps,
            y: chartData.cpu,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'CPU',
            line: { color: '#3498db', width: 2 },
            marker: { size: 4 }
        },
        {
            x: chartData.timestamps,
            y: chartData.memory,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Memory',
            line: { color: '#e74c3c', width: 2 },
            marker: { size: 4 }
        }
    ];
    
    Plotly.react('resource-chart', traces);
}
"""

def create_dashboard_handler(dashboard_data):
    """Create a handler class with dashboard data"""
    class Handler(DashboardHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, dashboard_data=dashboard_data, **kwargs)
    return Handler

def start_dashboard(port=8005, host='localhost'):
    """Start the web dashboard"""
    dashboard_data = DashboardData()
    dashboard_data.start_monitoring()
    
    # Create handler with dashboard data
    handler_class = create_dashboard_handler(dashboard_data)
    
    # Start server
    server = HTTPServer((host, port), handler_class)
    
    print(f"🚀 Starting RHEL Resource Manager Dashboard...")
    print(f"📊 Dashboard URL: http://{host}:{port}")
    print(f"⏱️  Auto-refresh: Every {dashboard_data.update_interval} seconds")
    print(f"🔄 Press Ctrl+C to stop")
    
    # Open browser
    try:
        webbrowser.open(f"http://{host}:{port}")
    except:
        print("Could not open browser automatically. Please open manually.")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopping dashboard...")
        dashboard_data.stop_monitoring()
        server.shutdown()
        print("✅ Dashboard stopped")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RHEL Resource Manager Web Dashboard')
    parser.add_argument('--port', type=int, default=8005, help='Port to run the dashboard on')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    
    args = parser.parse_args()
    
    start_dashboard(args.port, args.host)

if __name__ == "__main__":
    main() 