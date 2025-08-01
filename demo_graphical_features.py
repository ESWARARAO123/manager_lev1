#!/usr/bin/env python3.12
"""
Demo script for RHEL Resource Manager Graphical Features
This script demonstrates all the visualization capabilities
"""

import sys
import os
import time
import webbrowser
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_real_time_charts():
    """Demo the real-time charts functionality"""
    print("🚀 Demo: Real-time Interactive Charts")
    print("=" * 50)
    
    try:
        from scripts.real_time_charts import RealTimeCharts
        
        # Initialize charts
        charts = RealTimeCharts()
        
        # Start monitoring
        print("Starting real-time monitoring...")
        charts.start_monitoring(interval=2)
        
        # Collect some data
        print("Collecting data for 10 seconds...")
        time.sleep(10)
        
        # Generate charts
        print("Generating interactive charts...")
        
        # Dashboard
        dashboard = charts.create_dashboard_chart()
        charts.save_chart(dashboard, "demo_dashboard")
        print("✅ Dashboard chart created")
        
        # CPU chart
        cpu_chart = charts.create_cpu_chart()
        charts.save_chart(cpu_chart, "demo_cpu")
        print("✅ CPU usage chart created")
        
        # Memory chart
        memory_chart = charts.create_memory_chart()
        charts.save_chart(memory_chart, "demo_memory")
        print("✅ Memory usage chart created")
        
        # Process analysis
        process_chart = charts.create_process_chart()
        charts.save_chart(process_chart, "demo_processes")
        print("✅ Process analysis chart created")
        
        # System info
        system_chart = charts.create_system_info_chart()
        charts.save_chart(system_chart, "demo_system")
        print("✅ System info chart created")
        
        # Open dashboard in browser
        print("\n🌐 Opening dashboard in browser...")
        webbrowser.open(f"file://{os.path.abspath('demo_dashboard')}.html")
        
        print("\n📊 All charts generated successfully!")
        print("Files created:")
        print("  - demo_dashboard.html/png")
        print("  - demo_cpu.html/png")
        print("  - demo_memory.html/png")
        print("  - demo_processes.html/png")
        print("  - demo_system.html/png")
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Make sure all required packages are installed:")
        print("  pip install plotly psutil pandas")
    except Exception as e:
        print(f"❌ Error generating charts: {e}")

def demo_static_charts():
    """Demo the static chart generation"""
    print("\n📈 Demo: Static Chart Generation")
    print("=" * 50)
    
    try:
        from scripts.chart_generator import ChartGenerator
        
        # Architecture flowchart
        print("Generating architecture flowchart...")
        arch_data = {
            "components": [
                {"layer": "Data Collection", "tools": ["/proc filesystem", "psutil library", "systemd API"]},
                {"layer": "Resource Management", "tools": ["cgroups", "systemd units", "resource limits"]},
                {"layer": "Monitoring", "tools": ["real-time monitoring", "alerting system", "logging"]},
                {"layer": "Control Interface", "tools": ["web dashboard", "CLI commands", "REST API"]}
            ]
        }
        ChartGenerator.create_architecture_flowchart(arch_data, "demo_architecture")
        print("✅ Architecture flowchart created")
        
        # Resource manager flow
        print("Generating resource manager flow...")
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
        ChartGenerator.create_resource_flowchart(flow_data, "demo_resource_flow")
        print("✅ Resource manager flow created")
        
        print("\n📊 Static charts generated successfully!")
        print("Files created:")
        print("  - demo_architecture.png")
        print("  - demo_resource_flow.png")
        
    except ImportError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Error generating static charts: {e}")

def demo_enhanced_gui():
    """Demo the enhanced GUI"""
    print("\n🖥️ Demo: Enhanced GUI")
    print("=" * 50)
    
    try:
        import tkinter as tk
        from gui.enhanced_gui import EnhancedResourceManagerGUI
        
        print("Launching enhanced GUI...")
        print("Features available:")
        print("  - Real-time dashboard")
        print("  - CPU/Memory monitoring")
        print("  - Process analysis")
        print("  - System information")
        print("  - Data export")
        print("  - Report generation")
        
        root = tk.Tk()
        app = EnhancedResourceManagerGUI(root)
        
        # Start the GUI
        print("✅ Enhanced GUI launched successfully!")
        print("Use the buttons to explore different features.")
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Make sure tkinter is available")
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")

def demo_data_generation():
    """Demo data generation capabilities"""
    print("\n📊 Demo: Data Generation")
    print("=" * 50)
    
    try:
        from scripts.data_generator import DataGenerator
        
        print("Generating sample data...")
        
        # Generate system resource data
        system_data_file = DataGenerator.generate_system_resource_data()
        print(f"✅ Generated system resource data: {system_data_file}")
        
        # Generate process data
        process_data_file = DataGenerator.generate_process_data()
        print(f"✅ Generated process data: {process_data_file}")
        
        # Generate alert data
        alert_data_file = DataGenerator.generate_alert_data()
        print(f"✅ Generated alert data: {alert_data_file}")
        
        print("\n📁 Data files created:")
        print(f"  - {system_data_file}")
        print(f"  - {process_data_file}")
        print(f"  - {alert_data_file}")
        
    except ImportError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Error generating data: {e}")

def main():
    """Main demo function"""
    print("🎯 RHEL Resource Manager - Graphical Features Demo")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if required packages are available
    required_packages = ['plotly', 'psutil', 'pandas', 'matplotlib']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("⚠️  Warning: Some packages are missing:")
        for package in missing_packages:
            print(f"    - {package}")
        print("\nInstall missing packages with:")
        print(f"  pip install {' '.join(missing_packages)}")
        print()
    
    # Run demos
    try:
        # Demo 1: Real-time charts
        demo_real_time_charts()
        
        # Demo 2: Static charts
        demo_static_charts()
        
        # Demo 3: Data generation
        demo_data_generation()
        
        # Demo 4: Enhanced GUI (optional)
        print("\n" + "=" * 60)
        response = input("Would you like to launch the enhanced GUI? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            demo_enhanced_gui()
        
        print("\n🎉 Demo completed successfully!")
        print("Check the generated files in the current directory.")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")

if __name__ == "__main__":
    main() 