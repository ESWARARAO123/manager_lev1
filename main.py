#!/usr/bin/env python3.12
"""
Main entry point for RHEL Resource Manager
Coordinates all components and provides the main application interface
"""

import sys
import argparse
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any

# Configure logging first
try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/var/log/resource_manager.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
except PermissionError:
    # Fallback to console-only logging if file logging fails
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger('ResourceManager')

# Import our modular components with proper error handling
try:
    from core.resource_manager import ResourceManager
    from gui.headless_interface import HeadlessResourceManager
    from gui.gui_interface import ResourceManagerGUI
    from utils.cli_tool import ResourceManagerCLI
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    logger.warning(f"Some modules could not be imported: {e}")
    IMPORTS_SUCCESSFUL = False
    # Create dummy classes for graceful degradation
    class ResourceManager:
        def __init__(self):
            pass
        def get_system_status(self):
            return {"error": "ResourceManager not available"}
        def start_monitoring(self, interval):
            logger.warning("Monitoring not available")
        def stop_monitoring(self):
            pass
        def create_resource_group(self, name, cpu, memory):
            return False
    
    class HeadlessResourceManager:
        def __init__(self):
            pass
        def show_menu(self):
            print("Headless interface not available")
    
    class ResourceManagerGUI:
        def __init__(self, root):
            pass
    
    class ResourceManagerCLI:
        def __init__(self):
            pass
        def show_status(self):
            print("CLI tool not available")

class RHELResourceManager:
    """Main application class that coordinates all components"""
    
    def __init__(self):
        if IMPORTS_SUCCESSFUL:
            self.resource_manager = ResourceManager()
            self.cli = ResourceManagerCLI()
        else:
            self.resource_manager = ResourceManager()
            self.cli = ResourceManagerCLI()
        
    def run_cli(self, args: argparse.Namespace):
        """Run CLI mode"""
        try:
            if args.status:
                status = self.resource_manager.get_system_status()
                print(json.dumps(status, indent=2, default=str))
                
            elif args.create_group:
                if args.cpu_limit and args.memory_limit:
                    success = self.resource_manager.create_resource_group(
                        args.create_group, args.cpu_limit, args.memory_limit
                    )
                    print(f"Resource group creation: {'Success' if success else 'Failed'}")
                else:
                    print("Error: --cpu-limit and --memory-limit required for creating groups")
                    
            elif args.monitor:
                print(f"Starting monitoring with {args.interval}s interval...")
                self.resource_manager.start_monitoring(args.interval)
                
                try:
                    while True:
                        import time
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\nStopping monitoring...")
                    self.resource_manager.stop_monitoring()
                    
            else:
                # Use the CLI tool for interactive mode
                self.cli.show_status()
                
        except Exception as e:
            logger.error(f"Error in CLI mode: {e}")
            sys.exit(1)
    
    def run_gui(self, headless: bool = False, enhanced: bool = False, web: bool = False):
        """Run GUI mode"""
        try:
            if web:
                # Run web-based dashboard
                try:
                    from web_dashboard import start_dashboard
                    start_dashboard()
                except ImportError as e:
                    logger.error(f"Web dashboard not available: {e}")
                    print("Web dashboard not available")
                    
            elif headless:
                # Run headless console interface
                headless_manager = HeadlessResourceManager()
                headless_manager.show_menu()
            elif enhanced:
                # Run enhanced GUI with real-time charts
                try:
                    from gui.enhanced_gui import EnhancedResourceManagerGUI
                    import tkinter as tk
                    root = tk.Tk()
                    app = EnhancedResourceManagerGUI(root)
                    root.mainloop()
                except ImportError as e:
                    logger.error(f"Enhanced GUI not available: {e}")
                    print("Enhanced GUI not available")
            else:
                # Run standard graphical interface
                try:
                    import tkinter as tk
                    root = tk.Tk()
                    gui = ResourceManagerGUI(root)
                    root.mainloop()
                except Exception as e:
                    logger.error(f"Standard GUI not available: {e}")
                    print("Standard GUI not available")
                
        except Exception as e:
            logger.error(f"Error in GUI mode: {e}")
            print(f"Falling back to headless mode: {e}")
            self.run_gui(headless=True)
    
    def run_service(self, interval: int = 30):
        """Run as a service/daemon"""
        try:
            logger.info("Starting RHEL Resource Manager service...")
            self.resource_manager.start_monitoring(interval)
            
            # Keep the service running
            import time
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Stopping RHEL Resource Manager service...")
            self.resource_manager.stop_monitoring()
        except Exception as e:
            logger.error(f"Service error: {e}")
            sys.exit(1)
    
    def generate_data(self, data_type: str = "all"):
        """Generate sample data for testing"""
        try:
            from scripts.data_generator import DataGenerator
        except ImportError:
            logger.error("Data generator not available")
            print("Data generator not available")
            return
        
        try:
            if data_type in ["all", "system"]:
                DataGenerator.generate_system_resource_data()
            if data_type in ["all", "process"]:
                DataGenerator.generate_process_data()
            if data_type in ["all", "alert"]:
                DataGenerator.generate_alert_data()
            if data_type in ["all", "cgroup"]:
                DataGenerator.generate_cgroup_data()
                
            print("Data generation completed successfully!")
            
        except Exception as e:
            logger.error(f"Error generating data: {e}")
    
    def generate_charts(self, chart_type: str = "all"):
        """Generate charts and visualizations"""
        try:
            from scripts.chart_generator import ChartGenerator
        except ImportError:
            logger.error("Chart generator not available")
            print("Chart generator not available")
            return
        
        try:
            if chart_type in ["all", "architecture"]:
                # Architecture flowchart data
                arch_data = {
                    "components": [
                        {"layer": "Data Collection", "tools": ["/proc filesystem", "psutil library", "systemd API"]},
                        {"layer": "Resource Management", "tools": ["cgroups", "systemd units", "resource limits"]},
                        {"layer": "Monitoring", "tools": ["real-time monitoring", "alerting system", "logging"]},
                        {"layer": "Control Interface", "tools": ["web dashboard", "CLI commands", "REST API"]}
                    ]
                }
                ChartGenerator.create_architecture_flowchart(arch_data)
                
            if chart_type in ["all", "resource"]:
                # Resource manager deployment flow data
                flow_data = {
                    "steps": [
                        {"phase": "Setup", "step": "System Setup", "details": "Install deps, Check RHEL"}, 
                        {"phase": "Development", "step": "Core Dev", "details": "Python + psutil + cgroups"}, 
                        {"phase": "Configuration", "step": "Configuration", "details": "Config + systemd"}, 
                        {"phase": "Deployment", "step": "Installation", "details": "Deploy + Enable + Perms"}, 
                        {"phase": "Testing", "step": "Testing", "details": "Start + Test + Monitor"}, 
                        {"phase": "Management", "step": "Management", "details": "CLI + Dashboard + Alerts"}
                    ]
                }
                ChartGenerator.create_resource_flowchart(flow_data)
                
            if chart_type in ["all", "monitoring"]:
                # Generate monitoring chart from CSV data
                ChartGenerator.create_resource_monitoring_chart("system_resource_monitoring_data.csv")
                
            print("Chart generation completed successfully!")
            
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
    
    def discover_network(self, network_range: str, username: str, password: str = None):
        """Discover servers in the network"""
        try:
            from core.network_discovery import NetworkDiscovery
        except ImportError:
            logger.error("NetworkDiscovery module not available")
            print("NetworkDiscovery module not available. Install paramiko: pip install paramiko")
            return
        
        try:
            discovery = NetworkDiscovery()
            discovery.set_credentials(username, password)
            
            print(f"🔍 Discovering servers in network range: {network_range}")
            discovered = discovery.discover_network(network_range)
            
            if discovered:
                print(f"✅ Found {len(discovered)} servers:")
                for ip in discovered:
                    print(f"   📡 {ip}")
            else:
                print("❌ No servers discovered")
                
        except Exception as e:
            logger.error(f"Error discovering network: {e}")
            print(f"Error: {e}")
    
    def check_network_access(self, username: str, password: str = None):
        """Check SSH accessibility of discovered servers"""
        try:
            from core.network_discovery import NetworkDiscovery
        except ImportError:
            logger.error("NetworkDiscovery module not available")
            print("NetworkDiscovery module not available. Install paramiko: pip install paramiko")
            return
        
        try:
            discovery = NetworkDiscovery()
            discovery.set_credentials(username, password)
            
            # First discover servers if not already done
            if not discovery.discovered_servers:
                print("No servers discovered. Running discovery first...")
                discovery.discover_network("192.168.2.0/24")
            
            print("🔐 Checking SSH accessibility...")
            accessible = discovery.check_server_accessibility()
            
            if accessible:
                print(f"✅ {len(accessible)} servers are accessible:")
                for ip, info in accessible.items():
                    status = "✅" if info['accessible'] else "❌"
                    error = f" ({info['error']})" if info.get('error') else ""
                    print(f"   {status} {ip}{error}")
                    if info.get('system_info'):
                        print(f"      System: {info['system_info']}")
            else:
                print("❌ No servers are accessible")
                
        except Exception as e:
            logger.error(f"Error checking network access: {e}")
            print(f"Error: {e}")
    
    def monitor_multiple_servers(self):
        """Monitor multiple servers"""
        try:
            from core.network_discovery import NetworkDiscovery
        except ImportError:
            logger.error("NetworkDiscovery module not available")
            print("NetworkDiscovery module not available. Install paramiko: pip install paramiko")
            return
        
        try:
            discovery = NetworkDiscovery()
            
            if not discovery.accessible_servers:
                print("No accessible servers found. Run discovery and accessibility check first.")
                return
            
            print(f"📊 Starting monitoring of {len(discovery.accessible_servers)} servers")
            discovery.start_monitoring(interval=30)
            
            try:
                while True:
                    status_data = discovery.get_all_servers_status()
                    print(f"\n📊 Server Status - {datetime.now().strftime('%H:%M:%S')}")
                    print("-" * 60)
                    
                    for ip, status in status_data.get('server_status', {}).items():
                        cpu = status.get('cpu_usage', 0)
                        memory = status.get('memory_usage', {}).get('percent', 0)
                        print(f"{ip}: CPU {cpu:.1f}%, Memory {memory:.1f}%")
                    
                    time.sleep(30)
                    
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped")
                discovery.stop_monitoring()
                
        except Exception as e:
            logger.error(f"Error monitoring servers: {e}")
            print(f"Error: {e}")
    
    def run_multi_server_gui(self):
        """Run multi-server GUI dashboard"""
        try:
            from gui.multi_server_dashboard import MultiServerDashboard
            import tkinter as tk
            
            root = tk.Tk()
            app = MultiServerDashboard(root)
            root.mainloop()
            
        except ImportError as e:
            logger.error(f"Multi-server GUI not available: {e}")
            print("Multi-server GUI not available")
        except Exception as e:
            logger.error(f"Error launching multi-server GUI: {e}")
            print(f"Error: {e}")
    
    def test_specific_servers(self):
        """Test connectivity to local server and discover remote servers"""
        import subprocess
        import time
        
        print("🔍 Testing Server Connectivity")
        print("=" * 50)
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Get local server info
        from utils.network_utils import get_local_ip, get_hostname, get_network_ranges, discover_servers_in_network
        
        local_ip = get_local_ip()
        hostname = get_hostname()
        
        servers = {
            local_ip: f"Local Server ({hostname})"
        }
        
        # Discover servers in network
        print("🔍 Discovering servers in network...")
        network_ranges = get_network_ranges()
        discovered_servers = []
        
        for network_range in network_ranges[:2]:  # Limit to first 2 ranges for speed
            print(f"📡 Scanning {network_range}...")
            servers_in_range = discover_servers_in_network(network_range)
            discovered_servers.extend(servers_in_range)
        
        # Add discovered servers to the list
        for i, server_ip in enumerate(discovered_servers[:5]):  # Limit to first 5
            servers[server_ip] = f"Discovered Server {i+1}"
        
        results = {}
        
        for ip, name in servers.items():
            print(f"📡 Testing {name} ({ip})...")
            
            # Test ping
            try:
                ping_result = subprocess.run(
                    ['ping', '-c', '1', '-W', '2', ip],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                ping_ok = ping_result.returncode == 0
                print(f"   Ping: {'✅' if ping_ok else '❌'}")
            except:
                ping_ok = False
                print(f"   Ping: ❌")
            
            # Test SSH
            try:
                ssh_result = subprocess.run(
                    ['ssh', '-o', 'ConnectTimeout=5', '-o', 'BatchMode=yes', f'root@{ip}', 'echo "SSH test successful"'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                ssh_ok = ssh_result.returncode == 0
                print(f"   SSH: {'✅' if ssh_ok else '❌'}")
            except:
                ssh_ok = False
                print(f"   SSH: ❌")
            
            results[ip] = {
                'name': name,
                'ping': ping_ok,
                'ssh': ssh_ok
            }
            
            # Get system information if SSH is available
            if ssh_ok:
                print(f"   📊 Getting system information...")
                try:
                    from utils.network_utils import is_local_server
                    
                    if is_local_server(ip):
                        # Local server - use psutil
                        import psutil
                        info = {
                            'cpu_percent': psutil.cpu_percent(interval=1),
                            'memory_percent': psutil.virtual_memory().percent,
                            'disk_percent': psutil.disk_usage('/').percent,
                            'load_avg': psutil.getloadavg(),
                            'uptime': time.time() - psutil.boot_time()
                        }
                    else:
                        # Remote server - use SSH commands
                        # Get CPU usage
                        cpu_cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
                        cpu_result = subprocess.run(
                            ['ssh', f'root@{ip}', cpu_cmd],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        cpu_usage = float(cpu_result.stdout.strip()) if cpu_result.stdout.strip() else 0.0
                        
                        # Get memory usage
                        mem_cmd = "free -m | grep '^Mem:' | awk '{print $3/$2*100}'"
                        mem_result = subprocess.run(
                            ['ssh', f'root@{ip}', mem_cmd],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        memory_percent = float(mem_result.stdout.strip()) if mem_result.stdout.strip() else 0.0
                        
                        # Get disk usage
                        disk_cmd = "df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1"
                        disk_result = subprocess.run(
                            ['ssh', f'root@{ip}', disk_cmd],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        disk_percent = int(disk_result.stdout.strip()) if disk_result.stdout.strip() else 0
                        
                        # Get load average
                        load_cmd = "cat /proc/loadavg | awk '{print $1}'"
                        load_result = subprocess.run(
                            ['ssh', f'root@{ip}', load_cmd],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        load_avg = float(load_result.stdout.strip()) if load_result.stdout.strip() else 0.0
                        
                        info = {
                            'cpu_percent': cpu_usage,
                            'memory_percent': memory_percent,
                            'disk_percent': disk_percent,
                            'load_avg': [load_avg, 0.0, 0.0],
                            'uptime': 0  # Could add uptime command if needed
                        }
                    
                    results[ip]['info'] = info
                    print(f"   ✅ System info retrieved successfully")
                    
                except Exception as e:
                    print(f"   ❌ Error getting system info: {e}")
                    results[ip]['info'] = None
            
            print()
        
        # Display results
        print("📊 Test Results Summary")
        print("=" * 50)
        
        for ip, result in results.items():
            print(f"\n🏠 {result['name']} ({ip})")
            print(f"   Ping: {'✅' if result['ping'] else '❌'}")
            print(f"   SSH: {'✅' if result['ssh'] else '❌'}")
            
            if result.get('info'):
                info = result['info']
                print(f"   📈 System Status:")
                print(f"      CPU: {info['cpu_percent']:.1f}%")
                print(f"      Memory: {info['memory_percent']:.1f}%")
                print(f"      Disk: {info['disk_percent']}%")
                print(f"      Load: {info['load_avg'][0]:.2f}")
        
        print("\n" + "=" * 50)
        
        # Summary
        accessible_servers = [ip for ip, result in results.items() if result['ssh']]
        print(f"✅ Accessible servers: {len(accessible_servers)}")
        for ip in accessible_servers:
            print(f"   - {ip} ({results[ip]['name']})")
        
        if len(accessible_servers) > 0:
            print(f"\n🚀 Ready for multi-server monitoring!")
            print(f"Use: python3 main.py --multi-server-gui")
            print(f"Or: python3 main.py --multi-monitor")
            print(f"Or: python3 main.py --quick-status (no SSH prompts)")
    
    def run_quick_status(self):
        """Run quick status check without SSH prompts"""
        try:
            from quick_status import main as quick_status_main
            quick_status_main()
        except ImportError:
            print("Quick status module not available")
            print("Use: python3 quick_status.py")
        except Exception as e:
            logger.error(f"Error running quick status: {e}")
            print(f"Error: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='RHEL CPU and Memory Resource Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run CLI mode
  python -m rhel_resource_manager --status
  
  # Run GUI mode
  python -m rhel_resource_manager --gui
  
  # Run headless console mode
  python -m rhel_resource_manager --headless
  
  # Run as service
  python -m rhel_resource_manager --service --interval 30
  
  # Generate sample data
  python -m rhel_resource_manager --generate-data
  
  # Generate charts
  python -m rhel_resource_manager --generate-charts
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--cli', action='store_true', help='Run in CLI mode')
    mode_group.add_argument('--gui', action='store_true', help='Run in GUI mode')
    mode_group.add_argument('--enhanced-gui', action='store_true', help='Run in enhanced GUI mode with real-time charts')
    mode_group.add_argument('--web-dashboard', action='store_true', help='Run web-based dashboard with auto-refresh')
    mode_group.add_argument('--headless', action='store_true', help='Run in headless console mode')
    mode_group.add_argument('--service', action='store_true', help='Run as a service/daemon')
    
    # CLI options
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--monitor', action='store_true', help='Start monitoring mode')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds')
    parser.add_argument('--create-group', type=str, help='Create resource group')
    parser.add_argument('--cpu-limit', type=int, help='CPU limit (shares)')
    parser.add_argument('--memory-limit', type=str, help='Memory limit (e.g., 1G)')
    
    # Data and chart generation
    parser.add_argument('--generate-data', action='store_true', help='Generate sample data')
    parser.add_argument('--generate-charts', action='store_true', help='Generate charts')
    parser.add_argument('--data-type', choices=['all', 'system', 'process', 'alert', 'cgroup'], 
                       default='all', help='Type of data to generate')
    parser.add_argument('--chart-type', choices=['all', 'architecture', 'resource', 'monitoring'], 
                       default='all', help='Type of charts to generate')
    
    # Network discovery options
    parser.add_argument('--discover-network', action='store_true', help='Discover servers in network')
    parser.add_argument('--network-range', default='172.16.16.0/24', help='Network range to scan')
    parser.add_argument('--ssh-username', help='SSH username for server access')
    parser.add_argument('--ssh-password', help='SSH password for server access')
    parser.add_argument('--check-access', action='store_true', help='Check SSH accessibility of discovered servers')
    parser.add_argument('--multi-monitor', action='store_true', help='Monitor multiple servers')
    parser.add_argument('--multi-server-gui', action='store_true', help='Launch multi-server GUI dashboard')
    parser.add_argument('--test-servers', action='store_true', help='Test connectivity to local server and discover remote servers')
    parser.add_argument('--quick-status', action='store_true', help='Show quick status of both servers (no SSH prompts)')
    
    args = parser.parse_args()
    
    # Initialize the main application
    app = RHELResourceManager()
    
    try:
        # Determine mode and run appropriate interface
        if args.service:
            app.run_service(args.interval)
        elif args.web_dashboard:
            app.run_gui(web=True)
        elif args.enhanced_gui:
            app.run_gui(enhanced=True)
        elif args.gui:
            app.run_gui(headless=False)
        elif args.headless:
            app.run_gui(headless=True)
        elif args.generate_data:
            app.generate_data(args.data_type)
        elif args.generate_charts:
            app.generate_charts(args.chart_type)
        elif args.discover_network:
            app.discover_network(args.network_range, args.ssh_username, args.ssh_password)
        elif args.check_access:
            app.check_network_access(args.ssh_username, args.ssh_password)
        elif args.multi_monitor:
            app.monitor_multiple_servers()
        elif args.multi_server_gui:
            app.run_multi_server_gui()
        elif args.test_servers:
            app.test_specific_servers()
        elif args.quick_status:
            app.run_quick_status()
        elif args.cli or args.status or args.monitor or args.create_group:
            app.run_cli(args)
        else:
            # Default to web dashboard mode
            app.run_gui(web=True)
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 