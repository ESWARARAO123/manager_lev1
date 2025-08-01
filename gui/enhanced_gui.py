#!/usr/bin/env python3.12
"""
Enhanced GUI for RHEL Resource Manager
Web-based dashboard with real-time interactive charts
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import threading
import time
import json
import os
import sys
from datetime import datetime
import subprocess

# Import our chart modules
try:
    from ..scripts.real_time_charts import RealTimeCharts
    from ..scripts.chart_generator import ChartGenerator
except ImportError:
    try:
        from scripts.real_time_charts import RealTimeCharts
        from scripts.chart_generator import ChartGenerator
    except ImportError:
        print("Warning: Chart modules not found. Some features may not work.")

class EnhancedResourceManagerGUI:
    """Enhanced GUI with web-based dashboard integration"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("RHEL Resource Manager - Enhanced Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2c3e50')
        
        # Initialize chart system
        self.charts = RealTimeCharts()
        self.monitoring = False
        self.monitor_thread = None
        
        # Chart update interval
        self.update_interval = 5
        
        # Setup UI
        self.setup_ui()
        
        # Start initial data collection
        self.update_data()
    
    def setup_ui(self):
        """Setup the enhanced UI components"""
        # Main container
        main_container = tk.Frame(self.root, bg='#2c3e50')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_container, bg='#34495e', relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="🚀 RHEL Resource Manager - Enhanced Dashboard", 
                              font=('Arial', 24, 'bold'), bg='#34495e', fg='#ecf0f1')
        title_label.pack(pady=20)
        
        # Control panel
        control_frame = tk.Frame(main_container, bg='#34495e', relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg='#34495e')
        button_frame.pack(pady=10)
        
        # Style for buttons
        button_style = {
            'font': ('Arial', 12, 'bold'),
            'width': 18,
            'height': 2,
            'relief': tk.RAISED,
            'bd': 3
        }
        
        # Real-time Dashboard button
        self.dashboard_btn = tk.Button(
            button_frame, text="📊 Real-time Dashboard", 
            command=self.open_realtime_dashboard, 
            bg='#3498db', fg='white', **button_style
        )
        self.dashboard_btn.pack(side=tk.LEFT, padx=5)
        
        # CPU Monitor button
        self.cpu_btn = tk.Button(
            button_frame, text="💻 CPU Monitor", 
            command=self.open_cpu_monitor, 
            bg='#e74c3c', fg='white', **button_style
        )
        self.cpu_btn.pack(side=tk.LEFT, padx=5)
        
        # Memory Monitor button
        self.memory_btn = tk.Button(
            button_frame, text="🧠 Memory Monitor", 
            command=self.open_memory_monitor, 
            bg='#9b59b6', fg='white', **button_style
        )
        self.memory_btn.pack(side=tk.LEFT, padx=5)
        
        # Process Analysis button
        self.process_btn = tk.Button(
            button_frame, text="📋 Process Analysis", 
            command=self.open_process_analysis, 
            bg='#f39c12', fg='white', **button_style
        )
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        # System Info button
        self.system_btn = tk.Button(
            button_frame, text="⚙️ System Info", 
            command=self.open_system_info, 
            bg='#27ae60', fg='white', **button_style
        )
        self.system_btn.pack(side=tk.LEFT, padx=5)
        
        # Second row of buttons
        button_frame2 = tk.Frame(control_frame, bg='#34495e')
        button_frame2.pack(pady=10)
        
        # Start/Stop Monitoring button
        self.monitor_btn = tk.Button(
            button_frame2, text="▶️ Start Monitoring", 
            command=self.toggle_monitoring, 
            bg='#e67e22', fg='white', **button_style
        )
        self.monitor_btn.pack(side=tk.LEFT, padx=5)
        
        # Generate Reports button
        self.report_btn = tk.Button(
            button_frame2, text="📈 Generate Reports", 
            command=self.generate_reports, 
            bg='#16a085', fg='white', **button_style
        )
        self.report_btn.pack(side=tk.LEFT, padx=5)
        
        # Settings button
        self.settings_btn = tk.Button(
            button_frame2, text="🔧 Settings", 
            command=self.show_settings, 
            bg='#8e44ad', fg='white', **button_style
        )
        self.settings_btn.pack(side=tk.LEFT, padx=5)
        
        # Export Data button
        self.export_btn = tk.Button(
            button_frame2, text="💾 Export Data", 
            command=self.export_data, 
            bg='#2980b9', fg='white', **button_style
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # Content area
        content_frame = tk.Frame(main_container, bg='white', relief=tk.RAISED, bd=2)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Click a button to view detailed information")
        status_bar = tk.Label(
            main_container, textvariable=self.status_var, 
            bg='#2c3e50', fg='#ecf0f1', font=('Arial', 10)
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Quick stats frame
        self.setup_quick_stats(content_frame)
    
    def setup_quick_stats(self, parent):
        """Setup quick statistics display"""
        stats_frame = tk.Frame(parent, bg='#ecf0f1', relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Stats title
        stats_title = tk.Label(
            stats_frame, text="Quick System Statistics", 
            font=('Arial', 16, 'bold'), bg='#ecf0f1', fg='#2c3e50'
        )
        stats_title.pack(pady=(10, 5))
        
        # Stats grid
        stats_grid = tk.Frame(stats_frame, bg='#ecf0f1')
        stats_grid.pack(pady=10)
        
        # CPU stats
        cpu_frame = tk.Frame(stats_grid, bg='#3498db', relief=tk.RAISED, bd=2)
        cpu_frame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        self.cpu_label = tk.Label(
            cpu_frame, text="CPU Usage", 
            font=('Arial', 12, 'bold'), bg='#3498db', fg='white'
        )
        self.cpu_label.pack(pady=5)
        
        self.cpu_value = tk.Label(
            cpu_frame, text="0%", 
            font=('Arial', 20, 'bold'), bg='#3498db', fg='white'
        )
        self.cpu_value.pack(pady=5)
        
        # Memory stats
        memory_frame = tk.Frame(stats_grid, bg='#e74c3c', relief=tk.RAISED, bd=2)
        memory_frame.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        self.memory_label = tk.Label(
            memory_frame, text="Memory Usage", 
            font=('Arial', 12, 'bold'), bg='#e74c3c', fg='white'
        )
        self.memory_label.pack(pady=5)
        
        self.memory_value = tk.Label(
            memory_frame, text="0%", 
            font=('Arial', 20, 'bold'), bg='#e74c3c', fg='white'
        )
        self.memory_value.pack(pady=5)
        
        # Disk stats
        disk_frame = tk.Frame(stats_grid, bg='#27ae60', relief=tk.RAISED, bd=2)
        disk_frame.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        
        self.disk_label = tk.Label(
            disk_frame, text="Disk Usage", 
            font=('Arial', 12, 'bold'), bg='#27ae60', fg='white'
        )
        self.disk_label.pack(pady=5)
        
        self.disk_value = tk.Label(
            disk_frame, text="0%", 
            font=('Arial', 20, 'bold'), bg='#27ae60', fg='white'
        )
        self.disk_value.pack(pady=5)
        
        # Process stats
        process_frame = tk.Frame(stats_grid, bg='#f39c12', relief=tk.RAISED, bd=2)
        process_frame.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        
        self.process_label = tk.Label(
            process_frame, text="Active Processes", 
            font=('Arial', 12, 'bold'), bg='#f39c12', fg='white'
        )
        self.process_label.pack(pady=5)
        
        self.process_value = tk.Label(
            process_frame, text="0", 
            font=('Arial', 20, 'bold'), bg='#f39c12', fg='white'
        )
        self.process_value.pack(pady=5)
        
        # Configure grid weights
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)
        stats_grid.columnconfigure(2, weight=1)
        stats_grid.columnconfigure(3, weight=1)
    
    def update_data(self):
        """Update current system data"""
        try:
            import psutil
            
            # Update CPU usage
            cpu_percent = psutil.cpu_percent()
            self.cpu_value.config(text=f"{cpu_percent:.1f}%")
            
            # Update memory usage
            memory = psutil.virtual_memory()
            self.memory_value.config(text=f"{memory.percent:.1f}%")
            
            # Update disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.disk_value.config(text=f"{disk_percent:.1f}%")
            
            # Update process count
            process_count = len(psutil.pids())
            self.process_value.config(text=str(process_count))
            
            # Update status
            self.status_var.set(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.status_var.set(f"Error updating data: {e}")
    
    def open_realtime_dashboard(self):
        """Open real-time dashboard in browser"""
        try:
            self.status_var.set("Generating real-time dashboard...")
            
            # Create dashboard chart
            dashboard = self.charts.create_dashboard_chart()
            
            # Save and open in browser
            filename = "realtime_dashboard"
            self.charts.save_chart(dashboard, filename)
            
            # Open in browser
            webbrowser.open(f"file://{os.path.abspath(filename)}.html")
            
            self.status_var.set("Real-time dashboard opened in browser")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open dashboard: {e}")
            self.status_var.set("Error opening dashboard")
    
    def open_cpu_monitor(self):
        """Open CPU monitor in browser"""
        try:
            self.status_var.set("Generating CPU monitor...")
            
            cpu_chart = self.charts.create_cpu_chart()
            filename = "cpu_monitor"
            self.charts.save_chart(cpu_chart, filename)
            
            webbrowser.open(f"file://{os.path.abspath(filename)}.html")
            self.status_var.set("CPU monitor opened in browser")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open CPU monitor: {e}")
            self.status_var.set("Error opening CPU monitor")
    
    def open_memory_monitor(self):
        """Open memory monitor in browser"""
        try:
            self.status_var.set("Generating memory monitor...")
            
            memory_chart = self.charts.create_memory_chart()
            filename = "memory_monitor"
            self.charts.save_chart(memory_chart, filename)
            
            webbrowser.open(f"file://{os.path.abspath(filename)}.html")
            self.status_var.set("Memory monitor opened in browser")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open memory monitor: {e}")
            self.status_var.set("Error opening memory monitor")
    
    def open_process_analysis(self):
        """Open process analysis in browser"""
        try:
            self.status_var.set("Generating process analysis...")
            
            process_chart = self.charts.create_process_chart()
            filename = "process_analysis"
            self.charts.save_chart(process_chart, filename)
            
            webbrowser.open(f"file://{os.path.abspath(filename)}.html")
            self.status_var.set("Process analysis opened in browser")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open process analysis: {e}")
            self.status_var.set("Error opening process analysis")
    
    def open_system_info(self):
        """Open system info in browser"""
        try:
            self.status_var.set("Generating system info...")
            
            system_chart = self.charts.create_system_info_chart()
            filename = "system_info"
            self.charts.save_chart(system_chart, filename)
            
            webbrowser.open(f"file://{os.path.abspath(filename)}.html")
            self.status_var.set("System info opened in browser")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open system info: {e}")
            self.status_var.set("Error opening system info")
    
    def toggle_monitoring(self):
        """Toggle real-time monitoring"""
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        try:
            self.monitoring = True
            self.monitor_btn.config(text="⏹️ Stop Monitoring", bg='#c0392b')
            
            # Start monitoring thread
            self.monitor_thread = self.charts.start_monitoring(self.update_interval)
            
            # Start UI updates
            self.update_ui_loop()
            
            self.status_var.set("Real-time monitoring started")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring: {e}")
            self.status_var.set("Error starting monitoring")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        try:
            self.monitoring = False
            self.monitor_btn.config(text="▶️ Start Monitoring", bg='#e67e22')
            
            if self.monitor_thread:
                self.monitor_thread.join(timeout=1)
            
            self.status_var.set("Real-time monitoring stopped")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop monitoring: {e}")
            self.status_var.set("Error stopping monitoring")
    
    def update_ui_loop(self):
        """Update UI in a loop"""
        if self.monitoring:
            self.update_data()
            self.root.after(self.update_interval * 1000, self.update_ui_loop)
    
    def generate_reports(self):
        """Generate comprehensive reports"""
        try:
            self.status_var.set("Generating reports...")
            
            # Generate all chart types
            ChartGenerator.create_architecture_flowchart({})
            ChartGenerator.create_resource_flowchart({})
            ChartGenerator.create_resource_monitoring_chart("system_resource_monitoring_data.csv")
            
            # Generate real-time charts
            self.charts.save_chart(self.charts.create_dashboard_chart(), "comprehensive_report")
            
            messagebox.showinfo("Success", "Reports generated successfully!\nCheck the current directory for generated files.")
            self.status_var.set("Reports generated successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate reports: {e}")
            self.status_var.set("Error generating reports")
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg='#ecf0f1')
        
        # Settings content
        tk.Label(settings_window, text="Settings", font=('Arial', 16, 'bold'), 
                bg='#ecf0f1', fg='#2c3e50').pack(pady=20)
        
        # Update interval setting
        interval_frame = tk.Frame(settings_window, bg='#ecf0f1')
        interval_frame.pack(pady=10)
        
        tk.Label(interval_frame, text="Update Interval (seconds):", 
                bg='#ecf0f1', fg='#2c3e50').pack()
        
        interval_var = tk.StringVar(value=str(self.update_interval))
        interval_entry = tk.Entry(interval_frame, textvariable=interval_var, width=10)
        interval_entry.pack(pady=5)
        
        # Save button
        def save_settings():
            try:
                self.update_interval = int(interval_var.get())
                settings_window.destroy()
                messagebox.showinfo("Success", "Settings saved successfully!")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number for update interval")
        
        tk.Button(settings_window, text="Save Settings", command=save_settings,
                 bg='#27ae60', fg='white', font=('Arial', 12, 'bold')).pack(pady=20)
    
    def export_data(self):
        """Export monitoring data"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                # Export current data
                export_data = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_data": list(self.charts.cpu_data),
                    "memory_data": list(self.charts.memory_data),
                    "disk_data": list(self.charts.disk_data),
                    "network_data": list(self.charts.network_data),
                    "timestamps": [str(ts) for ts in self.charts.timestamps]
                }
                
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
                self.status_var.set("Data exported successfully")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")
            self.status_var.set("Error exporting data")

def main():
    """Main function to run the enhanced GUI"""
    root = tk.Tk()
    app = EnhancedResourceManagerGUI(root)
    
    # Start periodic updates
    def periodic_update():
        app.update_data()
        root.after(5000, periodic_update)  # Update every 5 seconds
    
    root.after(1000, periodic_update)
    
    root.mainloop()

if __name__ == "__main__":
    main() 