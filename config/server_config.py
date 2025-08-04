#!/usr/bin/env python3.12
"""
Server Configuration for Multi-Server Monitoring
Defines known servers and their connection details
"""

# Known servers in the network
KNOWN_SERVERS = {
    "172.16.16.21": {
        "name": "Local Server",
        "description": "Current server running the monitoring tool",
        "type": "local",
        "ssh_username": "root",
        "ssh_password": None,  # Will use current user's credentials
        "enabled": True
    },
    "172.16.16.23": {
        "name": "Remote Server",
        "description": "Remote server accessible via SSH",
        "type": "remote",
        "ssh_username": "root",
        "ssh_password": None,  # Will prompt for password
        "enabled": True
    }
}

# Network configuration
NETWORK_CONFIG = {
    "network_range": "172.16.16.0/24",
    "scan_timeout": 2,
    "ssh_timeout": 10,
    "monitoring_interval": 30
}

# SSH Configuration
SSH_CONFIG = {
    "default_username": "root",
    "key_file": None,  # Path to SSH key file if using key-based auth
    "banner_timeout": 10,
    "auth_timeout": 10
}

def get_known_servers():
    """Get list of known servers"""
    return [ip for ip, config in KNOWN_SERVERS.items() if config.get('enabled', True)]

def get_server_config(ip):
    """Get configuration for a specific server"""
    return KNOWN_SERVERS.get(ip, {})

def get_network_range():
    """Get the network range to scan"""
    return NETWORK_CONFIG.get("network_range", "172.16.16.0/24")

def get_ssh_config():
    """Get SSH configuration"""
    return SSH_CONFIG.copy() 