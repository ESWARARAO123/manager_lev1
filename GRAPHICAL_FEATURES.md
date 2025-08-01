# RHEL Resource Manager - Graphical Features

This document describes the comprehensive graphical visualization capabilities of the RHEL Resource Manager.

## 🎯 Overview

The RHEL Resource Manager now includes powerful graphical features that provide:

- **Real-time interactive charts** using Plotly
- **Enhanced GUI dashboard** with web-based visualizations
- **Static chart generation** for reports and documentation
- **Process analysis** with visual representations
- **System monitoring** with live updates

## 📊 Available Visualization Types

### 1. Real-time Interactive Charts

#### Dashboard Chart
- **File**: `real_time_charts.py`
- **Features**: 
  - Multi-panel dashboard with 6 subplots
  - CPU, Memory, Disk, and Network usage
  - System load averages
  - Active process count
  - Real-time data updates
  - Interactive hover information

#### CPU Usage Chart
- **Features**:
  - Line chart with area fill
  - Warning and critical threshold lines
  - Real-time CPU percentage tracking
  - Interactive zoom and pan

#### Memory Usage Chart
- **Features**:
  - Memory usage over time
  - Threshold indicators
  - Percentage-based visualization
  - Color-coded alerts

#### Process Analysis Chart
- **Features**:
  - Top 10 processes by resource usage
  - CPU and Memory comparison
  - Grouped bar chart
  - Process name truncation for readability

#### System Information Gauges
- **Features**:
  - Three gauge indicators (CPU, Memory, Disk)
  - Color-coded ranges (green/yellow/red)
  - Percentage displays
  - Threshold warnings

### 2. Static Chart Generation

#### Architecture Flowchart
- **File**: `chart_generator.py`
- **Features**:
  - System architecture visualization
  - Layer-based design
  - Component relationships
  - Tool mapping

#### Resource Manager Flowchart
- **Features**:
  - Deployment process flow
  - Phase-based visualization
  - Step-by-step process
  - Timeline representation

#### Monitoring Charts
- **Features**:
  - Historical data visualization
  - CSV data import
  - Time-series analysis
  - Resource usage trends

### 3. Enhanced GUI Interface

#### Main Dashboard
- **File**: `enhanced_gui.py`
- **Features**:
  - Modern dark theme
  - Quick statistics display
  - Real-time data updates
  - Multiple view options

#### Control Panel
- **Features**:
  - One-click chart generation
  - Browser integration
  - Export capabilities
  - Settings management

## 🚀 How to Use

### Quick Start

1. **Run the Enhanced GUI**:
   ```bash
   python -m rhel_resource_manager --enhanced-gui
   ```

2. **Generate Real-time Charts**:
   ```bash
   python -m rhel_resource_manager --generate-charts
   ```

3. **Run the Demo**:
   ```bash
   python demo_graphical_features.py
   ```

### Command Line Options

```bash
# Enhanced GUI with real-time charts
python -m rhel_resource_manager --enhanced-gui

# Standard GUI
python -m rhel_resource_manager --gui

# Generate specific chart types
python -m rhel_resource_manager --generate-charts --chart-type monitoring

# Generate sample data
python -m rhel_resource_manager --generate-data
```

### Programmatic Usage

#### Real-time Charts
```python
from scripts.real_time_charts import RealTimeCharts

# Initialize charts
charts = RealTimeCharts()

# Start monitoring
charts.start_monitoring(interval=5)

# Create dashboard
dashboard = charts.create_dashboard_chart()
charts.save_chart(dashboard, "my_dashboard")

# Open in browser
import webbrowser
webbrowser.open("my_dashboard.html")
```

#### Static Charts
```python
from scripts.chart_generator import ChartGenerator

# Create architecture chart
arch_data = {
    "components": [
        {"layer": "Data Collection", "tools": ["psutil", "systemd"]},
        {"layer": "Management", "tools": ["cgroups", "limits"]}
    ]
}
ChartGenerator.create_architecture_flowchart(arch_data, "architecture.png")
```

## 📁 File Structure

```
rhel_resource_manager/
├── scripts/
│   ├── real_time_charts.py      # Real-time interactive charts
│   ├── chart_generator.py       # Static chart generation
│   └── data_generator.py        # Sample data generation
├── gui/
│   ├── enhanced_gui.py          # Enhanced GUI with charts
│   ├── gui_interface.py         # Standard GUI
│   └── headless_interface.py    # Console interface
├── demo_graphical_features.py   # Demo script
└── GRAPHICAL_FEATURES.md        # This documentation
```

## 🎨 Chart Customization

### Color Schemes
All charts use a consistent color scheme:
- **CPU**: Blue (#1f77b4)
- **Memory**: Orange (#ff7f0e)
- **Disk**: Green (#2ca02c)
- **Network**: Red (#d62728)

### Thresholds
Default thresholds for alerts:
- **Warning**: 80%
- **Critical**: 95%

### Chart Templates
- **Plotly White**: Clean, professional appearance
- **Responsive**: Adapts to different screen sizes
- **Interactive**: Hover effects and zoom capabilities

## 🔧 Configuration

### Update Intervals
- **Real-time monitoring**: 2-10 seconds
- **Data collection**: 5-60 seconds
- **Chart updates**: Configurable via GUI

### Export Options
- **HTML**: Interactive web-based charts
- **PNG**: Static image files
- **JSON**: Raw data export
- **CSV**: Time-series data

## 🌐 Browser Integration

### Automatic Browser Launch
Charts are automatically opened in the default web browser for:
- Real-time dashboards
- Process analysis
- System information
- Generated reports

### Browser Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Local file access (for HTML files)

## 📈 Performance Considerations

### Data Management
- **Circular buffers**: Prevent memory overflow
- **Configurable limits**: Adjustable data points
- **Efficient updates**: Minimal resource usage

### Chart Optimization
- **Lazy loading**: Charts generated on demand
- **Caching**: Reuse chart objects
- **Background processing**: Non-blocking updates

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   pip install plotly psutil pandas matplotlib
   ```

2. **Browser Not Opening**:
   - Check file permissions
   - Verify browser is installed
   - Use manual file opening

3. **Charts Not Updating**:
   - Check monitoring status
   - Verify data collection
   - Restart monitoring

4. **Memory Issues**:
   - Reduce update frequency
   - Limit data points
   - Close unused charts

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Example Outputs

### Real-time Dashboard
- Multi-panel layout
- Live data streams
- Interactive controls
- Threshold indicators

### Process Analysis
- Top resource consumers
- CPU vs Memory comparison
- Process identification
- Resource allocation

### System Gauges
- Current usage levels
- Color-coded status
- Percentage displays
- Warning thresholds

## 🔮 Future Enhancements

### Planned Features
- **WebSocket integration**: Real-time updates
- **Custom dashboards**: User-defined layouts
- **Alert integration**: Visual notifications
- **Historical analysis**: Trend visualization
- **Export scheduling**: Automated reports

### API Extensions
- **REST API**: Chart generation endpoints
- **Webhook support**: External integrations
- **Plugin system**: Custom chart types
- **Template engine**: Customizable layouts

## 📚 Additional Resources

### Documentation
- [Plotly Documentation](https://plotly.com/python/)
- [psutil Documentation](https://psutil.readthedocs.io/)
- [RHEL System Administration](https://access.redhat.com/documentation/)

### Examples
- `demo_graphical_features.py`: Complete demo
- `scripts/real_time_charts.py`: Chart implementations
- `gui/enhanced_gui.py`: GUI integration

### Support
- Check the main README for installation instructions
- Review error logs for troubleshooting
- Use the demo script for testing

---

**Note**: The graphical features require Python packages: `plotly`, `psutil`, `pandas`, and `matplotlib`. Install them using:
```bash
pip install plotly psutil pandas matplotlib
``` 