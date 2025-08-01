# RHEL Resource Manager - Web Dashboard

## 🎯 Overview

The RHEL Resource Manager now includes a **web-based dashboard** that automatically updates every 5 seconds and displays all system information on a single page. This provides a modern, responsive interface for monitoring your RHEL system resources in real-time.

## 🚀 Features

### **Real-time Monitoring**
- **Auto-refresh**: Updates every 5 seconds automatically
- **Live data**: Real-time CPU, Memory, Disk, and Network usage
- **Interactive charts**: Plotly-based visualizations
- **System alerts**: Automatic detection and display of resource warnings

### **Comprehensive Dashboard**
- **Quick Stats**: CPU, Memory, Disk usage with visual indicators
- **System Information**: Hostname, platform, uptime, load averages
- **Process Analysis**: Top 10 processes by resource usage
- **Network Monitoring**: Bytes sent/received, interface count
- **Alert System**: Real-time alerts for high resource usage

### **Modern Interface**
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Theme**: Professional appearance with gradient backgrounds
- **Interactive Elements**: Hover effects and smooth animations
- **Color-coded Alerts**: Visual indicators for resource status

## 🛠️ Installation & Setup

### **Prerequisites**
```bash
# Install required packages
pip install plotly psutil pandas
```

### **Quick Start**

#### **Method 1: Direct Launch**
```bash
# Navigate to the rhel_resource_manager directory
cd rhel_resource_manager

# Run the web dashboard
python start_dashboard.py
```

#### **Method 2: Using Main Application**
```bash
# Run with web dashboard mode
python -m rhel_resource_manager --web-dashboard

# Or just run without arguments (defaults to web dashboard)
python -m rhel_resource_manager
```

#### **Method 3: Custom Port**
```bash
# Run on a specific port
python web_dashboard.py --port 9090 --host 0.0.0.0
```

## 📊 Dashboard Components

### **1. Header Section**
- **Title**: RHEL Resource Manager - Live Dashboard
- **Status Indicator**: Shows online/offline status
- **Last Update**: Timestamp of last data refresh

### **2. Quick Stats Grid**
- **CPU Usage**: Real-time percentage with color-coded bar
- **Memory Usage**: Current memory utilization
- **Disk Usage**: Root filesystem usage
- **Active Processes**: Count of running processes

### **3. Resource Chart**
- **Interactive Plotly Chart**: CPU and Memory usage over time
- **Real-time Updates**: Chart updates with new data points
- **Zoom & Pan**: Interactive chart controls
- **Hover Information**: Detailed tooltips

### **4. Information Panels**
- **System Information**: Hostname, platform, CPU cores, uptime, load averages
- **Top Processes**: Top 10 processes by CPU and Memory usage
- **Network Information**: Bytes sent/received, interface count
- **Alerts**: Real-time system alerts and warnings

## 🎨 Visual Features

### **Color Coding**
- **🟢 Green**: Normal usage (0-70%)
- **🟡 Yellow**: Warning level (70-90%)
- **🔴 Red**: Critical level (90-100%)

### **Alert System**
- **Warning Alerts**: CPU/Memory/Disk > 80%
- **Visual Indicators**: Color-coded borders and text
- **Real-time Updates**: Alerts appear/disappear automatically

### **Responsive Design**
- **Desktop**: Full dashboard with all panels
- **Tablet**: Optimized layout for medium screens
- **Mobile**: Single-column layout for small screens

## 🔧 Configuration

### **Update Intervals**
The dashboard updates every 5 seconds by default. You can modify this in the `web_dashboard.py` file:

```python
# In DashboardData.__init__()
self.update_interval = 5  # seconds
```

### **Port Configuration**
```bash
# Default: localhost:8080
python web_dashboard.py --port 9090 --host 0.0.0.0
```

### **Custom Styling**
You can customize the appearance by modifying the CSS in the `_get_css()` method of `DashboardHandler`.

## 📱 Browser Compatibility

### **Supported Browsers**
- **Chrome**: Full support
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support

### **Requirements**
- **JavaScript**: Must be enabled
- **Local Access**: For file:// URLs
- **Network Access**: For remote monitoring

## 🔄 Auto-refresh Mechanism

### **How It Works**
1. **Background Thread**: Data collection runs in a separate thread
2. **JavaScript Polling**: Frontend polls for updates every 5 seconds
3. **Real-time Charts**: Plotly charts update with new data points
4. **Status Indicators**: Visual feedback for connection status

### **Data Flow**
```
System Monitoring → Background Thread → JSON API → JavaScript → Dashboard Update
```

## 🛡️ Security Considerations

### **Local Access Only**
- Dashboard runs on localhost by default
- No external network access
- Suitable for local system monitoring

### **Network Access**
If you need remote access:
```bash
# Bind to all interfaces (use with caution)
python web_dashboard.py --host 0.0.0.0 --port 8080
```

## 📈 Performance

### **Resource Usage**
- **CPU**: Minimal impact (< 1% typical)
- **Memory**: ~50-100MB for dashboard
- **Network**: Local HTTP traffic only

### **Optimization**
- **Efficient Polling**: 5-second intervals
- **Data Buffering**: Limited to recent data points
- **Background Processing**: Non-blocking updates

## 🚨 Troubleshooting

### **Common Issues**

#### **1. Dashboard Won't Start**
```bash
# Check if port is in use
netstat -tulpn | grep 8080

# Try different port
python web_dashboard.py --port 9090
```

#### **2. Browser Won't Open**
```bash
# Manual access
# Open browser and go to: http://localhost:8080
```

#### **3. No Data Updates**
```bash
# Check system permissions
sudo python web_dashboard.py

# Check psutil installation
pip install --upgrade psutil
```

#### **4. Charts Not Loading**
```bash
# Check internet connection (for Plotly CDN)
# Check browser console for errors
```

### **Debug Mode**
```python
# Add to web_dashboard.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔮 Future Enhancements

### **Planned Features**
- **WebSocket Support**: Real-time push updates
- **Custom Dashboards**: User-defined layouts
- **Historical Data**: Long-term trend analysis
- **Export Features**: PDF/PNG report generation
- **Authentication**: User login system
- **Multi-system Monitoring**: Monitor multiple servers

### **API Extensions**
- **REST API**: External integrations
- **Webhook Support**: Alert notifications
- **Plugin System**: Custom widgets
- **Template Engine**: Customizable themes

## 📚 Usage Examples

### **Basic Monitoring**
```bash
# Start dashboard
python start_dashboard.py

# Access in browser
# http://localhost:8080
```

### **Remote Monitoring**
```bash
# Allow remote access
python web_dashboard.py --host 0.0.0.0 --port 8080

# Access from another machine
# http://your-server-ip:8080
```

### **Custom Configuration**
```python
# Modify update interval
# Edit web_dashboard.py line 35
self.update_interval = 10  # 10 seconds

# Modify port
# Edit web_dashboard.py line 836
def start_dashboard(port=9090, host='localhost'):
```

## 🎯 Best Practices

### **Production Use**
1. **Use HTTPS**: For remote access
2. **Set up Authentication**: For security
3. **Monitor Resource Usage**: Dashboard itself
4. **Regular Updates**: Keep dependencies current
5. **Backup Configuration**: Save custom settings

### **Development**
1. **Test Different Browsers**: Ensure compatibility
2. **Check Mobile Responsiveness**: Test on devices
3. **Monitor Performance**: Watch resource usage
4. **Log Issues**: Keep track of problems

---

**The web dashboard provides a modern, automated way to monitor your RHEL system resources with real-time updates and beautiful visualizations!** 