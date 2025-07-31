#!/usr/bin/env python3.12
"""
RHEL Resource Manager Package
A comprehensive system resource management tool for Red Hat Enterprise Linux
"""

__version__ = "1.0.0"
__author__ = "System Administrator"
__license__ = "MIT"

# Import main classes for easy access
from .core.resource_manager import ResourceManager
from .core.system_monitor import SystemMonitor
from .core.cgroup_manager import CgroupManager
from .core.systemd_manager import SystemdManager
from .core.alert_manager import AlertManager
from .gui.headless_interface import HeadlessResourceManager
from .gui.gui_interface import ResourceManagerGUI
from .utils.cli_tool import ResourceManagerCLI

# Main entry points
def main():
    """Main entry point for the application"""
    from .main import main as app_main
    app_main()

def cli_main():
    """CLI entry point"""
    from .utils.cli_tool import main as cli_main
    cli_main()

def gui_main():
    """GUI entry point"""
    from .gui.gui_interface import main as gui_main
    gui_main()

def headless_main():
    """Headless interface entry point"""
    from .gui.headless_interface import main as headless_main
    headless_main()

__all__ = [
    'ResourceManager',
    'SystemMonitor', 
    'CgroupManager',
    'SystemdManager',
    'AlertManager',
    'HeadlessResourceManager',
    'ResourceManagerGUI',
    'ResourceManagerCLI',
    'main',
    'cli_main',
    'gui_main',
    'headless_main'
] 