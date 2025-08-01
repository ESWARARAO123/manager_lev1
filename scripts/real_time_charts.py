#!/usr/bin/env python3.12
"""
Real-time interactive charts for RHEL Resource Manager
Provides live updating charts using Plotly for better visualization
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import psutil
import threading
import time
from collections import deque
from typing import Dict, List, Any, Optional
import json

class RealTimeCharts:
    """Real-time interactive charts for resource monitoring"""
    
    def __init__(self, max_points: int = 100):
        self.max_points = max_points
        self.cpu_data = deque(maxlen=max_points)
        self.memory_data = deque(maxlen=max_points)
        self.disk_data = deque(maxlen=max_points)
        self.network_data = deque(maxlen=max_points)
        self.timestamps = deque(maxlen=max_points)
        
        # Initialize with current data
        self.update_data()
    
    def update_data(self):
        """Update current system data"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network usage
            network = psutil.net_io_counters()
            network_total = network.bytes_sent + network.bytes_recv
            
            # Timestamp
            timestamp = datetime.now()
            
            # Store data
            self.cpu_data.append(cpu_percent)
            self.memory_data.append(memory_percent)
            self.disk_data.append(disk_percent)
            self.network_data.append(network_total)
            self.timestamps.append(timestamp)
            
        except Exception as e:
            print(f"Error updating data: {e}")
    
    def create_dashboard_chart(self) -> go.Figure:
        """Create comprehensive dashboard with multiple subplots"""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('CPU Usage', 'Memory Usage', 'Disk Usage', 'Network I/O', 'System Load', 'Process Count'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]],
            vertical_spacing=0.08,
            horizontal_spacing=0.08
        )
        
        # Convert deques to lists for plotting
        timestamps = list(self.timestamps)
        cpu_values = list(self.cpu_data)
        memory_values = list(self.memory_data)
        disk_values = list(self.disk_data)
        network_values = list(self.network_data)
        
        if not timestamps:
            return fig
        
        # CPU Usage (row 1, col 1)
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=cpu_values,
                mode='lines+markers',
                name='CPU %',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=4)
            ),
            row=1, col=1
        )
        
        # Memory Usage (row 1, col 2)
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=memory_values,
                mode='lines+markers',
                name='Memory %',
                line=dict(color='#ff7f0e', width=2),
                marker=dict(size=4)
            ),
            row=1, col=2
        )
        
        # Disk Usage (row 2, col 1)
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=disk_values,
                mode='lines+markers',
                name='Disk %',
                line=dict(color='#2ca02c', width=2),
                marker=dict(size=4)
            ),
            row=2, col=1
        )
        
        # Network I/O (row 2, col 2)
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=network_values,
                mode='lines+markers',
                name='Network Bytes',
                line=dict(color='#d62728', width=2),
                marker=dict(size=4)
            ),
            row=2, col=2
        )
        
        # System Load (row 3, col 1)
        try:
            load_avg = psutil.getloadavg()
            fig.add_trace(
                go.Bar(
                    x=['1min', '5min', '15min'],
                    y=load_avg,
                    name='Load Average',
                    marker_color=['#9467bd', '#8c564b', '#e377c2']
                ),
                row=3, col=1
            )
        except:
            pass
        
        # Process Count (row 3, col 2)
        try:
            process_count = len(psutil.pids())
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=process_count,
                    title={'text': "Active Processes"},
                    gauge={'axis': {'range': [None, 1000]},
                           'bar': {'color': "#17a2b8"},
                           'steps': [
                               {'range': [0, 200], 'color': "lightgray"},
                               {'range': [200, 500], 'color': "yellow"},
                               {'range': [500, 1000], 'color': "red"}
                           ]},
                ),
                row=3, col=2
            )
        except:
            pass
        
        # Update layout
        fig.update_layout(
            title="RHEL Resource Manager - Real-time Dashboard",
            height=800,
            showlegend=False,
            template="plotly_white"
        )
        
        # Update axes
        fig.update_xaxes(title_text="Time", row=1, col=1)
        fig.update_xaxes(title_text="Time", row=1, col=2)
        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_xaxes(title_text="Time", row=2, col=2)
        
        fig.update_yaxes(title_text="Usage %", range=[0, 100], row=1, col=1)
        fig.update_yaxes(title_text="Usage %", range=[0, 100], row=1, col=2)
        fig.update_yaxes(title_text="Usage %", range=[0, 100], row=2, col=1)
        fig.update_yaxes(title_text="Bytes", row=2, col=2)
        
        return fig
    
    def create_cpu_chart(self) -> go.Figure:
        """Create detailed CPU usage chart"""
        timestamps = list(self.timestamps)
        cpu_values = list(self.cpu_data)
        
        if not timestamps:
            return go.Figure()
        
        fig = go.Figure()
        
        # CPU usage line
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=cpu_values,
            mode='lines+markers',
            name='CPU Usage',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=6),
            fill='tonexty',
            fillcolor='rgba(31, 119, 180, 0.2)'
        ))
        
        # Add threshold lines
        fig.add_hline(y=80, line_dash="dash", line_color="orange", 
                     annotation_text="Warning (80%)")
        fig.add_hline(y=95, line_dash="dash", line_color="red", 
                     annotation_text="Critical (95%)")
        
        # Update layout
        fig.update_layout(
            title="Real-time CPU Usage",
            xaxis_title="Time",
            yaxis_title="CPU Usage (%)",
            yaxis=dict(range=[0, 100]),
            template="plotly_white",
            height=500
        )
        
        return fig
    
    def create_memory_chart(self) -> go.Figure:
        """Create detailed memory usage chart"""
        timestamps = list(self.timestamps)
        memory_values = list(self.memory_data)
        
        if not timestamps:
            return go.Figure()
        
        fig = go.Figure()
        
        # Memory usage line
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=memory_values,
            mode='lines+markers',
            name='Memory Usage',
            line=dict(color='#ff7f0e', width=3),
            marker=dict(size=6),
            fill='tonexty',
            fillcolor='rgba(255, 127, 14, 0.2)'
        ))
        
        # Add threshold lines
        fig.add_hline(y=80, line_dash="dash", line_color="orange", 
                     annotation_text="Warning (80%)")
        fig.add_hline(y=95, line_dash="dash", line_color="red", 
                     annotation_text="Critical (95%)")
        
        # Update layout
        fig.update_layout(
            title="Real-time Memory Usage",
            xaxis_title="Time",
            yaxis_title="Memory Usage (%)",
            yaxis=dict(range=[0, 100]),
            template="plotly_white",
            height=500
        )
        
        return fig
    
    def create_process_chart(self) -> go.Figure:
        """Create process analysis chart"""
        try:
            # Get top processes by CPU usage
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage and get top 10
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            top_processes = processes[:10]
            
            # Create bar chart
            fig = go.Figure()
            
            names = [p['name'][:20] for p in top_processes]  # Truncate long names
            cpu_values = [p['cpu_percent'] for p in top_processes]
            memory_values = [p['memory_percent'] for p in top_processes]
            
            fig.add_trace(go.Bar(
                x=names,
                y=cpu_values,
                name='CPU %',
                marker_color='#1f77b4'
            ))
            
            fig.add_trace(go.Bar(
                x=names,
                y=memory_values,
                name='Memory %',
                marker_color='#ff7f0e'
            ))
            
            fig.update_layout(
                title="Top 10 Processes by Resource Usage",
                xaxis_title="Process Name",
                yaxis_title="Usage %",
                barmode='group',
                template="plotly_white",
                height=500
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating process chart: {e}")
            return go.Figure()
    
    def create_system_info_chart(self) -> go.Figure:
        """Create system information gauge chart"""
        try:
            # Get system information
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Create subplots for gauges
            fig = make_subplots(
                rows=1, cols=3,
                subplot_titles=('CPU Usage', 'Memory Usage', 'Disk Usage'),
                specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]]
            )
            
            # CPU gauge
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=cpu_percent,
                title={'text': "CPU"},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "#1f77b4"},
                       'steps': [
                           {'range': [0, 50], 'color': "lightgreen"},
                           {'range': [50, 80], 'color': "yellow"},
                           {'range': [80, 100], 'color': "red"}
                       ],
                       'threshold': {
                           'line': {'color': "red", 'width': 4},
                           'thickness': 0.75,
                           'value': 90
                       }}
            ), row=1, col=1)
            
            # Memory gauge
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=memory.percent,
                title={'text': "Memory"},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "#ff7f0e"},
                       'steps': [
                           {'range': [0, 50], 'color': "lightgreen"},
                           {'range': [50, 80], 'color': "yellow"},
                           {'range': [80, 100], 'color': "red"}
                       ],
                       'threshold': {
                           'line': {'color': "red", 'width': 4},
                           'thickness': 0.75,
                           'value': 90
                       }}
            ), row=1, col=2)
            
            # Disk gauge
            disk_percent = (disk.used / disk.total) * 100
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=disk_percent,
                title={'text': "Disk"},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "#2ca02c"},
                       'steps': [
                           {'range': [0, 50], 'color': "lightgreen"},
                           {'range': [50, 80], 'color': "yellow"},
                           {'range': [80, 100], 'color': "red"}
                       ],
                       'threshold': {
                           'line': {'color': "red", 'width': 4},
                           'thickness': 0.75,
                           'value': 90
                       }}
            ), row=1, col=3)
            
            fig.update_layout(
                title="System Resource Gauges",
                template="plotly_white",
                height=400
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating system info chart: {e}")
            return go.Figure()
    
    def save_chart(self, fig: go.Figure, filename: str):
        """Save chart to file"""
        try:
            fig.write_html(f"{filename}.html")
            fig.write_image(f"{filename}.png")
            print(f"Chart saved as {filename}.html and {filename}.png")
        except Exception as e:
            print(f"Error saving chart: {e}")
    
    def start_monitoring(self, interval: int = 5):
        """Start continuous monitoring in a separate thread"""
        def monitor_loop():
            while True:
                self.update_data()
                time.sleep(interval)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        return monitor_thread

def main():
    """Demo function to show real-time charts"""
    charts = RealTimeCharts()
    
    # Start monitoring
    charts.start_monitoring(interval=2)
    
    # Create and display charts
    print("Creating real-time charts...")
    
    # Dashboard
    dashboard = charts.create_dashboard_chart()
    charts.save_chart(dashboard, "real_time_dashboard")
    
    # CPU chart
    cpu_chart = charts.create_cpu_chart()
    charts.save_chart(cpu_chart, "cpu_usage")
    
    # Memory chart
    memory_chart = charts.create_memory_chart()
    charts.save_chart(memory_chart, "memory_usage")
    
    # Process chart
    process_chart = charts.create_process_chart()
    charts.save_chart(process_chart, "process_analysis")
    
    # System info
    system_chart = charts.create_system_info_chart()
    charts.save_chart(system_chart, "system_info")
    
    print("Charts generated successfully!")
    print("Open the HTML files in your browser to view interactive charts.")

if __name__ == "__main__":
    main() 