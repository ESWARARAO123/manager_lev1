#!/usr/bin/env python3.12
"""
Multi-Server Dashboard GUI
Displays status of multiple servers across the network
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
from datetime import datetime
from typing import Dict, List

try:
    from core.network_discovery import NetworkDiscovery
except ImportError:
    print("Warning: NetworkDiscovery module not available")

class MultiServerDashboard:
    """Multi-server monitoring dashboard"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("RHEL Resource Manager - Multi-Server Dashboard")
        self.root.geometry("1200x800")
        
        # Initialize network discovery
        try:
            self.network_discovery = NetworkDiscovery()
        except:
            self.network_discovery = None
            messagebox.showerror("Error", "NetworkDiscovery module not available")
        
        self.running = False
        self.update_thread = None
        
        self.setup_ui()
        self.setup_menu()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Control panel
        self.setup_control_panel(main_frame)
        
        # Server status panel
        self.setup_server_panel(main_frame)
        
        # Status bar
        self.setup_status_bar(main_frame)
        
    def setup_control_panel(self, parent):
        """Setup the control panel"""
        control_frame = ttk.LabelFrame(parent, text="Network Discovery Controls", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Network range input
        ttk.Label(control_frame, text="Network Range:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.network_range_var = tk.StringVar(value="192.168.2.0/24")
        self.network_range_entry = ttk.Entry(control_frame, textvariable=self.network_range_var, width=20)
        self.network_range_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # Credentials
        ttk.Label(control_frame, text="Username:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.username_var = tk.StringVar(value="root")
        self.username_entry = ttk.Entry(control_frame, textvariable=self.username_var, width=15)
        self.username_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=(10, 0))
        
        self.discover_btn = ttk.Button(button_frame, text="🔍 Discover Network", command=self.discover_network)
        self.discover_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.check_access_btn = ttk.Button(button_frame, text="🔐 Check Access", command=self.check_accessibility)
        self.check_access_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.start_monitor_btn = ttk.Button(button_frame, text="▶️ Start Monitoring", command=self.start_monitoring)
        self.start_monitor_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_monitor_btn = ttk.Button(button_frame, text="⏹️ Stop Monitoring", command=self.stop_monitoring)
        self.stop_monitor_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.export_btn = ttk.Button(button_frame, text="💾 Export Results", command=self.export_results)
        self.export_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status indicators
        status_frame = ttk.Frame(control_frame)
        status_frame.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        
        self.discovered_label = ttk.Label(status_frame, text="Discovered: 0 servers")
        self.discovered_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.accessible_label = ttk.Label(status_frame, text="Accessible: 0 servers")
        self.accessible_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.monitoring_label = ttk.Label(status_frame, text="Monitoring: Stopped")
        self.monitoring_label.pack(side=tk.LEFT)
        
    def setup_server_panel(self, parent):
        """Setup the server status panel"""
        # Server list frame
        server_frame = ttk.LabelFrame(parent, text="Server Status", padding="10")
        server_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        server_frame.columnconfigure(0, weight=1)
        server_frame.rowconfigure(0, weight=1)
        
        # Create treeview for servers
        columns = ('IP Address', 'Status', 'CPU %', 'Memory %', 'Disk %', 'Load Avg', 'Uptime', 'Last Update')
        self.server_tree = ttk.Treeview(server_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.server_tree.heading(col, text=col)
            self.server_tree.column(col, width=120, minwidth=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(server_frame, orient=tk.VERTICAL, command=self.server_tree.yview)
        h_scrollbar = ttk.Scrollbar(server_frame, orient=tk.HORIZONTAL, command=self.server_tree.xview)
        self.server_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.server_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind double-click event
        self.server_tree.bind('<Double-1>', self.show_server_details)
        
    def setup_status_bar(self, parent):
        """Setup the status bar"""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
    def setup_menu(self):
        """Setup the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Results", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Set Credentials", command=self.set_credentials)
        tools_menu.add_command(label="Network Discovery", command=self.discover_network)
        tools_menu.add_command(label="Check Accessibility", command=self.check_accessibility)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def discover_network(self):
        """Discover servers in the network"""
        if not self.network_discovery:
            messagebox.showerror("Error", "NetworkDiscovery not available")
            return
        
        def discover_thread():
            try:
                self.status_var.set("Discovering network...")
                self.discover_btn.config(state='disabled')
                
                network_range = self.network_range_var.get()
                discovered = self.network_discovery.discover_network(network_range)
                
                self.root.after(0, lambda: self.update_discovery_status(discovered))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Discovery failed: {e}"))
            finally:
                self.root.after(0, lambda: self.discover_btn.config(state='normal'))
        
        threading.Thread(target=discover_thread, daemon=True).start()
    
    def update_discovery_status(self, discovered):
        """Update discovery status display"""
        self.discovered_label.config(text=f"Discovered: {len(discovered)} servers")
        self.status_var.set(f"Discovery completed. Found {len(discovered)} servers")
        
        # Clear and repopulate server tree
        for item in self.server_tree.get_children():
            self.server_tree.delete(item)
        
        for ip in discovered:
            self.server_tree.insert('', 'end', values=(ip, 'Discovered', '', '', '', '', '', ''))
    
    def check_accessibility(self):
        """Check SSH accessibility of discovered servers"""
        if not self.network_discovery:
            messagebox.showerror("Error", "NetworkDiscovery not available")
            return
        
        def check_thread():
            try:
                self.status_var.set("Checking server accessibility...")
                self.check_access_btn.config(state='disabled')
                
                accessible = self.network_discovery.check_server_accessibility()
                
                self.root.after(0, lambda: self.update_accessibility_status(accessible))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Accessibility check failed: {e}"))
            finally:
                self.root.after(0, lambda: self.check_access_btn.config(state='normal'))
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def update_accessibility_status(self, accessible):
        """Update accessibility status display"""
        self.accessible_label.config(text=f"Accessible: {len(accessible)} servers")
        self.status_var.set(f"Accessibility check completed. {len(accessible)} servers accessible")
        
        # Update server tree with accessibility status
        for item in self.server_tree.get_children():
            ip = self.server_tree.item(item)['values'][0]
            if ip in accessible:
                self.server_tree.set(item, 'Status', 'Accessible')
            else:
                self.server_tree.set(item, 'Status', 'Not Accessible')
    
    def start_monitoring(self):
        """Start monitoring all accessible servers"""
        if not self.network_discovery:
            messagebox.showerror("Error", "NetworkDiscovery not available")
            return
        
        if not self.network_discovery.accessible_servers:
            messagebox.showwarning("Warning", "No accessible servers found. Run discovery and accessibility check first.")
            return
        
        self.running = True
        self.network_discovery.start_monitoring(interval=30)  # Update every 30 seconds
        self.start_monitor_btn.config(state='disabled')
        self.stop_monitor_btn.config(state='normal')
        self.monitoring_label.config(text="Monitoring: Running")
        self.status_var.set("Monitoring started")
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_server_status, daemon=True)
        self.update_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if self.network_discovery:
            self.network_discovery.stop_monitoring()
        
        self.start_monitor_btn.config(state='normal')
        self.stop_monitor_btn.config(state='disabled')
        self.monitoring_label.config(text="Monitoring: Stopped")
        self.status_var.set("Monitoring stopped")
    
    def update_server_status(self):
        """Update server status display"""
        while self.running:
            try:
                if self.network_discovery:
                    status_data = self.network_discovery.get_all_servers_status()
                    
                    self.root.after(0, lambda: self.update_server_tree(status_data))
                
                time.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                print(f"Error updating server status: {e}")
                time.sleep(30)
    
    def update_server_tree(self, status_data):
        """Update the server tree with current status"""
        server_status = status_data.get('server_status', {})
        
        for item in self.server_tree.get_children():
            ip = self.server_tree.item(item)['values'][0]
            
            if ip in server_status:
                status = server_status[ip]
                
                # Format values
                cpu = f"{status.get('cpu_usage', 0):.1f}%"
                memory = f"{status.get('memory_usage', {}).get('percent', 0):.1f}%"
                disk = f"{status.get('disk_usage', {}).get('percent', 0)}%"
                load_avg = f"{status.get('load_average', [0, 0, 0])[0]:.2f}"
                uptime = status.get('uptime', 'Unknown')
                timestamp = status.get('timestamp', '').strftime('%H:%M:%S') if status.get('timestamp') else ''
                
                self.server_tree.set(item, 'CPU %', cpu)
                self.server_tree.set(item, 'Memory %', memory)
                self.server_tree.set(item, 'Disk %', disk)
                self.server_tree.set(item, 'Load Avg', load_avg)
                self.server_tree.set(item, 'Uptime', uptime)
                self.server_tree.set(item, 'Last Update', timestamp)
                self.server_tree.set(item, 'Status', 'Online')
        
        self.status_var.set(f"Last update: {datetime.now().strftime('%H:%M:%S')}")
    
    def show_server_details(self, event):
        """Show detailed information for a selected server"""
        selection = self.server_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        ip = self.server_tree.item(item)['values'][0]
        
        if self.network_discovery and ip in self.network_discovery.scan_results:
            status = self.network_discovery.scan_results[ip]
            self.show_details_window(ip, status)
    
    def show_details_window(self, ip, status):
        """Show detailed server information in a new window"""
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Server Details - {ip}")
        details_window.geometry("600x500")
        
        # Create text widget
        text_widget = tk.Text(details_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Format and display status information
        details = f"""Server Details for {ip}
{'='*50}

Timestamp: {status.get('timestamp', 'Unknown')}

CPU Usage: {status.get('cpu_usage', 0):.1f}%

Memory Usage:
  Total: {status.get('memory_usage', {}).get('total_mb', 0)} MB
  Used: {status.get('memory_usage', {}).get('used_mb', 0)} MB
  Free: {status.get('memory_usage', {}).get('free_mb', 0)} MB
  Percentage: {status.get('memory_usage', {}).get('percent', 0):.1f}%

Disk Usage:
  Filesystem: {status.get('disk_usage', {}).get('filesystem', 'Unknown')}
  Total: {status.get('disk_usage', {}).get('total', 'Unknown')}
  Used: {status.get('disk_usage', {}).get('used', 'Unknown')}
  Available: {status.get('disk_usage', {}).get('available', 'Unknown')}
  Percentage: {status.get('disk_usage', {}).get('percent', 0)}%

Load Average: {status.get('load_average', [0, 0, 0])}

Uptime: {status.get('uptime', 'Unknown')}

Network Interfaces:
{status.get('network_interfaces', {}).get('interfaces', 'Unknown')}
"""
        
        text_widget.insert(tk.END, details)
        text_widget.config(state=tk.DISABLED)
    
    def set_credentials(self):
        """Set SSH credentials"""
        if not self.network_discovery:
            messagebox.showerror("Error", "NetworkDiscovery not available")
            return
        
        username = simpledialog.askstring("Credentials", "Enter SSH username:", initialvalue=self.username_var.get())
        if username:
            password = simpledialog.askstring("Credentials", "Enter SSH password (leave empty for key-based auth):", show='*')
            self.network_discovery.set_credentials(username, password)
            self.username_var.set(username)
            messagebox.showinfo("Success", "Credentials set successfully")
    
    def export_results(self):
        """Export monitoring results"""
        if not self.network_discovery:
            messagebox.showerror("Error", "NetworkDiscovery not available")
            return
        
        try:
            filename = self.network_discovery.export_results()
            messagebox.showinfo("Success", f"Results exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", 
                          "RHEL Resource Manager - Multi-Server Dashboard\n\n"
                          "Version: 1.0\n"
                          "Features:\n"
                          "• Network discovery\n"
                          "• SSH accessibility checking\n"
                          "• Real-time server monitoring\n"
                          "• Resource usage tracking\n"
                          "• Results export")

def main():
    """Main function"""
    root = tk.Tk()
    app = MultiServerDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main() 