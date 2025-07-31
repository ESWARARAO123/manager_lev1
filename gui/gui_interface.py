#!/usr/bin/env python3.12
"""
RHEL Resource Manager GUI Application
Interactive GUI for monitoring CPU and Memory resources with real-time visualizations
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import psutil
import threading
import time
import json
import subprocess
import sys
from datetime import datetime, timedelta
from collections import deque
import numpy as np

class ResourceManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RHEL Resource Manager - GUI Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Data storage for real-time monitoring
        self.cpu_data = deque(maxlen=100)
        self.memory_data = deque(maxlen=100)
        self.timestamps = deque(maxlen=100)
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        
        # Current view
        self.current_view = "dashboard"
        
        # Initialize components
        self.setup_ui()
        self.setup_charts()
        
        # Start initial data collection
        self.update_data()
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="RHEL Resource Manager Dashboard", 
                              font=('Arial', 20, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Control buttons frame
        control_frame = tk.Frame(main_frame, bg='#f0f0f0')
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Style for buttons
        button_style = {'font': ('Arial', 12, 'bold'), 'width': 15, 'height': 2}
        
        # Dashboard button
        self.dashboard_btn = tk.Button(control_frame, text="📊 Dashboard", 
                                      command=self.show_dashboard, bg='#3498db', fg='white', **button_style)
        self.dashboard_btn.pack(side=tk.LEFT, padx=5)
        
        # CPU button
        self.cpu_btn = tk.Button(control_frame, text="💻 CPU Monitor", 
                                command=self.show_cpu_view, bg='#e74c3c', fg='white', **button_style)
        self.cpu_btn.pack(side=tk.LEFT, padx=5)
        
        # Memory button
        self.memory_btn = tk.Button(control_frame, text="🧠 Memory Monitor", 
                                   command=self.show_memory_view, bg='#9b59b6', fg='white', **button_style)
        self.memory_btn.pack(side=tk.LEFT, padx=5)
        
        # Start/Stop monitoring button
        self.monitor_btn = tk.Button(control_frame, text="▶️ Start Monitoring", 
                                    command=self.toggle_monitoring, bg='#27ae60', fg='white', **button_style)
        self.monitor_btn.pack(side=tk.LEFT, padx=5)
        
        # Settings button
        self.settings_btn = tk.Button(control_frame, text="⚙️ Settings", 
                                     command=self.show_settings, bg='#f39c12', fg='white', **button_style)
        self.settings_btn.pack(side=tk.LEFT, padx=5)
        
        # Content area
        self.content_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Click a button to view detailed information")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, 
                             bg='#34495e', fg='white', font=('Arial', 10))
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def setup_charts(self):
        """Setup matplotlib charts"""
        # Create figure with subplots
        self.fig = Figure(figsize=(12, 8), facecolor='white')
        
        # Dashboard subplots
        self.dashboard_ax1 = self.fig.add_subplot(2, 2, 1)  # CPU usage
        self.dashboard_ax2 = self.fig.add_subplot(2, 2, 2)  # Memory usage
        self.dashboard_ax3 = self.fig.add_subplot(2, 2, 3)  # Combined chart
        self.dashboard_ax4 = self.fig.add_subplot(2, 2, 4)  # System info
        
        # CPU detailed view
        self.cpu_ax = self.fig.add_subplot(111)
        
        # Memory detailed view
        self.memory_ax = self.fig.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.content_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def show_dashboard(self):
        """Show the main dashboard view"""
        self.current_view = "dashboard"
        self.status_var.set("Dashboard View - System Overview")
        self.update_dashboard()
        
    def show_cpu_view(self):
        """Show detailed CPU monitoring view"""
        self.current_view = "cpu"
        self.status_var.set("CPU Monitor - Detailed CPU Analysis")
        self.update_cpu_view()
        
    def show_memory_view(self):
        """Show detailed memory monitoring view"""
        self.current_view = "memory"
        self.status_var.set("Memory Monitor - Detailed Memory Analysis")
        self.update_memory_view()
        
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg='#f0f0f0')
        
        # Settings content
        tk.Label(settings_window, text="Resource Manager Settings", 
                font=('Arial', 16, 'bold'), bg='#f0f0f0').pack(pady=20)
        
        # Update interval setting
        tk.Label(settings_window, text="Update Interval (seconds):", bg='#f0f0f0').pack()
        interval_var = tk.StringVar(value="5")
        interval_entry = tk.Entry(settings_window, textvariable=interval_var)
        interval_entry.pack(pady=5)
        
        # Threshold settings
        tk.Label(settings_window, text="CPU Warning Threshold (%):", bg='#f0f0f0').pack()
        cpu_threshold_var = tk.StringVar(value="80")
        cpu_entry = tk.Entry(settings_window, textvariable=cpu_threshold_var)
        cpu_entry.pack(pady=5)
        
        tk.Label(settings_window, text="Memory Warning Threshold (%):", bg='#f0f0f0').pack()
        mem_threshold_var = tk.StringVar(value="80")
        mem_entry = tk.Entry(settings_window, textvariable=mem_threshold_var)
        mem_entry.pack(pady=5)
        
        # Save button
        tk.Button(settings_window, text="Save Settings", 
                 command=lambda: self.save_settings(interval_var.get(), 
                                                  cpu_threshold_var.get(), 
                                                  mem_threshold_var.get())).pack(pady=20)
        
    def save_settings(self, interval, cpu_threshold, mem_threshold):
        """Save application settings"""
        try:
            settings = {
                'update_interval': int(interval),
                'cpu_threshold': float(cpu_threshold),
                'memory_threshold': float(mem_threshold)
            }
            
            with open('/opt/resource_manager/gui_settings.json', 'w') as f:
                json.dump(settings, f)
                
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            
    def toggle_monitoring(self):
        """Toggle real-time monitoring on/off"""
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def start_monitoring(self):
        """Start real-time monitoring"""
        self.monitoring = True
        self.monitor_btn.config(text="⏹️ Stop Monitoring", bg='#e74c3c')
        self.status_var.set("Real-time monitoring started")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring = False
        self.monitor_btn.config(text="▶️ Start Monitoring", bg='#27ae60')
        self.status_var.set("Real-time monitoring stopped")
        
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            self.update_data()
            time.sleep(5)  # Update every 5 seconds
            
    def update_data(self):
        """Update system data"""
        try:
            # Get current timestamp
            now = datetime.now()
            
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Store data
            self.timestamps.append(now)
            self.cpu_data.append(cpu_percent)
            self.memory_data.append(memory_percent)
            
            # Update display based on current view
            if self.current_view == "dashboard":
                self.update_dashboard()
            elif self.current_view == "cpu":
                self.update_cpu_view()
            elif self.current_view == "memory":
                self.update_memory_view()
                
        except Exception as e:
            print(f"Error updating data: {e}")
            
    def update_dashboard(self):
        """Update dashboard view"""
        self.fig.clear()
        
        # Create subplots
        ax1 = self.fig.add_subplot(2, 2, 1)  # CPU
        ax2 = self.fig.add_subplot(2, 2, 2)  # Memory
        ax3 = self.fig.add_subplot(2, 2, 3)  # Combined
        ax4 = self.fig.add_subplot(2, 2, 4)  # System info
        
        if len(self.timestamps) > 0:
            # CPU Chart
            ax1.plot(list(self.timestamps), list(self.cpu_data), 'r-', linewidth=2, label='CPU Usage')
            ax1.set_title('CPU Usage Over Time', fontsize=12, fontweight='bold')
            ax1.set_ylabel('CPU Usage (%)')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Memory Chart
            ax2.plot(list(self.timestamps), list(self.memory_data), 'b-', linewidth=2, label='Memory Usage')
            ax2.set_title('Memory Usage Over Time', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Memory Usage (%)')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            
            # Combined Chart
            ax3.plot(list(self.timestamps), list(self.cpu_data), 'r-', linewidth=2, label='CPU')
            ax3.plot(list(self.timestamps), list(self.memory_data), 'b-', linewidth=2, label='Memory')
            ax3.set_title('Combined Resource Usage', fontsize=12, fontweight='bold')
            ax3.set_ylabel('Usage (%)')
            ax3.grid(True, alpha=0.3)
            ax3.legend()
            
        # System Information
        ax4.axis('off')
        system_info = self.get_system_info()
        info_text = "System Information:\n\n"
        for key, value in system_info.items():
            info_text += f"{key}: {value}\n"
        
        ax4.text(0.1, 0.9, info_text, transform=ax4.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace')
        
        self.fig.tight_layout()
        self.canvas.draw()
        
    def update_cpu_view(self):
        """Update CPU detailed view"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        if len(self.timestamps) > 0:
            # CPU usage line
            ax.plot(list(self.timestamps), list(self.cpu_data), 'r-', linewidth=3, label='CPU Usage')
            
            # Add threshold line
            ax.axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='Warning Threshold (80%)')
            ax.axhline(y=90, color='red', linestyle='--', alpha=0.7, label='Critical Threshold (90%)')
            
            # Fill area under curve
            ax.fill_between(list(self.timestamps), list(self.cpu_data), alpha=0.3, color='red')
            
            ax.set_title('CPU Usage Monitor', fontsize=16, fontweight='bold')
            ax.set_xlabel('Time')
            ax.set_ylabel('CPU Usage (%)')
            ax.grid(True, alpha=0.3)
            ax.legend()
            ax.set_ylim(0, 100)
            
        # Add CPU statistics
        if len(self.cpu_data) > 0:
            stats_text = f"Current CPU: {self.cpu_data[-1]:.1f}%\n"
            stats_text += f"Average CPU: {np.mean(list(self.cpu_data)):.1f}%\n"
            stats_text += f"Max CPU: {np.max(list(self.cpu_data)):.1f}%\n"
            stats_text += f"Min CPU: {np.min(list(self.cpu_data)):.1f}%"
            
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=12,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        self.fig.tight_layout()
        self.canvas.draw()
        
    def update_memory_view(self):
        """Update memory detailed view"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        if len(self.timestamps) > 0:
            # Memory usage line
            ax.plot(list(self.timestamps), list(self.memory_data), 'b-', linewidth=3, label='Memory Usage')
            
            # Add threshold line
            ax.axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='Warning Threshold (80%)')
            ax.axhline(y=90, color='red', linestyle='--', alpha=0.7, label='Critical Threshold (90%)')
            
            # Fill area under curve
            ax.fill_between(list(self.timestamps), list(self.memory_data), alpha=0.3, color='blue')
            
            ax.set_title('Memory Usage Monitor', fontsize=16, fontweight='bold')
            ax.set_xlabel('Time')
            ax.set_ylabel('Memory Usage (%)')
            ax.grid(True, alpha=0.3)
            ax.legend()
            ax.set_ylim(0, 100)
            
        # Add memory statistics
        if len(self.memory_data) > 0:
            memory = psutil.virtual_memory()
            stats_text = f"Current Memory: {self.memory_data[-1]:.1f}%\n"
            stats_text += f"Total Memory: {memory.total / (1024**3):.1f} GB\n"
            stats_text += f"Available: {memory.available / (1024**3):.1f} GB\n"
            stats_text += f"Used: {memory.used / (1024**3):.1f} GB"
            
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=12,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        self.fig.tight_layout()
        self.canvas.draw()
        
    def get_system_info(self):
        """Get system information"""
        try:
            # CPU info
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory info
            memory = psutil.virtual_memory()
            
            # Disk info
            disk = psutil.disk_usage('/')
            
            # System info
            system_info = {
                'CPU Cores': cpu_count,
                'CPU Frequency': f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A",
                'Total Memory': f"{memory.total / (1024**3):.1f} GB",
                'Available Memory': f"{memory.available / (1024**3):.1f} GB",
                'Total Disk': f"{disk.total / (1024**3):.1f} GB",
                'Free Disk': f"{disk.free / (1024**3):.1f} GB",
                'System Load': f"{psutil.getloadavg()[0]:.2f}"
            }
            
            return system_info
            
        except Exception as e:
            return {'Error': str(e)}

def main():
    """Main function"""
    root = tk.Tk()
    app = ResourceManagerGUI(root)
    
    # Configure matplotlib style
    plt.style.use('default')
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main() 