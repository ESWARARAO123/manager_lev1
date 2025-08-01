#!/usr/bin/env python3.12
"""
Main entry point for RHEL Resource Manager
Coordinates all components and provides the main application interface
"""

import sys
import argparse
import json
import logging
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