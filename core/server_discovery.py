#!/usr/bin/env python3.12
"""
Server Discovery and Management Module
Discovers servers in the network and manages SSH connections
"""

import subprocess
import socket
import threading
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import ipaddress

class ServerDiscovery:
    def __init__(self):
        self.discovered_servers = {}  # {ip: {'status': 'discovered', 'ssh_connected': False, 'info': {}}}
        self.connected_servers = {}   # {ip: {'ssh_connected': True, 'info': {}, 'last_check': datetime}}
        self.scanning = False
        
        # Get dynamic network ranges
        try:
            from utils.network_utils import get_network_ranges
            self.network_ranges = get_network_ranges()
        except ImportError:
            # Fallback to default ranges
            self.network_ranges = ['192.168.1.0/24', '10.0.0.0/8', '172.16.0.0/12']
        
    def scan_network(self, network_range: str = None) -> Dict[str, dict]:
        """Scan network for active servers"""
        if network_range:
            ranges = [network_range]
        else:
            ranges = self.network_ranges
            
        self.scanning = True
        discovered = {}
        
        print(f"🔍 Scanning networks: {ranges}")
        
        for network in ranges:
            try:
                network_obj = ipaddress.IPv4Network(network, strict=False)
                print(f"📡 Scanning {network} ({network_obj.num_addresses} addresses)")
                
                # Use threading to speed up scanning
                threads = []
                results = {}
                
                def scan_ip(ip):
                    if self._ping_host(str(ip)):
                        results[str(ip)] = {
                            'status': 'discovered',
                            'ssh_connected': False,
                            'discovered_at': datetime.now().isoformat(),
                            'network': network
                        }
                
                # Create threads for each IP
                for ip in network_obj.hosts():
                    if not self.scanning:  # Allow stopping the scan
                        break
                    thread = threading.Thread(target=scan_ip, args=(ip,))
                    threads.append(thread)
                    thread.start()
                    
                    # Limit concurrent threads
                    if len(threads) >= 50:
                        for t in threads:
                            t.join()
                        threads = []
                
                # Wait for remaining threads
                for t in threads:
                    t.join()
                
                discovered.update(results)
                
            except Exception as e:
                print(f"❌ Error scanning {network}: {e}")
        
        self.scanning = False
        self.discovered_servers.update(discovered)
        
        print(f"✅ Discovered {len(discovered)} servers")
        return discovered
    
    def _ping_host(self, ip: str) -> bool:
        """Ping a single host to check if it's alive"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1', ip],
                capture_output=True,
                text=True,
                timeout=3
            )
            return result.returncode == 0
        except:
            return False
    
    def test_ssh_connection(self, ip: str, username: str = 'root', password: str = None) -> bool:
        """Test SSH connection to a server"""
        try:
            if password:
                # Use sshpass for password authentication
                result = subprocess.run([
                    'sshpass', '-p', password,
                    'ssh', '-o', 'ConnectTimeout=5',
                    '-o', 'StrictHostKeyChecking=no',
                    f'{username}@{ip}', 'echo "SSH test successful"'
                ], capture_output=True, text=True, timeout=10)
            else:
                # Try key-based authentication
                result = subprocess.run([
                    'ssh', '-o', 'ConnectTimeout=5',
                    '-o', 'BatchMode=yes',
                    f'{username}@{ip}', 'echo "SSH test successful"'
                ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
        except:
            return False
    
    def connect_to_server(self, ip: str, username: str = 'root', password: str = None) -> bool:
        """Establish SSH connection to a server"""
        if self.test_ssh_connection(ip, username, password):
            # Get server information
            server_info = self._get_server_info(ip, username, password)
            
            self.connected_servers[ip] = {
                'ssh_connected': True,
                'username': username,
                'password': password,  # Store for future use
                'info': server_info,
                'connected_at': datetime.now().isoformat(),
                'last_check': datetime.now().isoformat()
            }
            
            # Update discovered servers
            if ip in self.discovered_servers:
                self.discovered_servers[ip]['ssh_connected'] = True
                self.discovered_servers[ip]['info'] = server_info
            
            print(f"✅ Connected to {ip}")
            return True
        else:
            print(f"❌ Failed to connect to {ip}")
            return False
    
    def _get_server_info(self, ip: str, username: str, password: str = None) -> dict:
        """Get basic server information via SSH"""
        try:
            if password:
                ssh_prefix = f'sshpass -p "{password}" ssh -o StrictHostKeyChecking=no {username}@{ip}'
            else:
                ssh_prefix = f'ssh -o BatchMode=yes {username}@{ip}'
            
            # Get hostname
            hostname_cmd = f'{ssh_prefix} "hostname"'
            hostname_result = subprocess.run(hostname_cmd, shell=True, capture_output=True, text=True, timeout=10)
            hostname = hostname_result.stdout.strip() if hostname_result.returncode == 0 else ip
            
            # Get OS info
            os_cmd = f'{ssh_prefix} "cat /etc/os-release | grep PRETTY_NAME | cut -d\\"\\" -f2"'
            os_result = subprocess.run(os_cmd, shell=True, capture_output=True, text=True, timeout=10)
            os_info = os_result.stdout.strip() if os_result.returncode == 0 else "Unknown"
            
            # Get CPU info
            cpu_cmd = f'{ssh_prefix} "nproc"'
            cpu_result = subprocess.run(cpu_cmd, shell=True, capture_output=True, text=True, timeout=10)
            cpu_cores = cpu_result.stdout.strip() if cpu_result.returncode == 0 else "Unknown"
            
            return {
                'hostname': hostname,
                'os': os_info,
                'cpu_cores': cpu_cores,
                'ip': ip,
                'status': 'Online'
            }
            
        except Exception as e:
            return {
                'hostname': ip,
                'os': 'Unknown',
                'cpu_cores': 'Unknown',
                'ip': ip,
                'status': 'Error',
                'error': str(e)
            }
    
    def disconnect_from_server(self, ip: str) -> bool:
        """Disconnect from a server"""
        if ip in self.connected_servers:
            del self.connected_servers[ip]
            
            if ip in self.discovered_servers:
                self.discovered_servers[ip]['ssh_connected'] = False
            
            print(f"✅ Disconnected from {ip}")
            return True
        return False
    
    def get_connected_servers_info(self) -> dict:
        """Get information from all connected servers"""
        servers_info = {}
        
        for ip, connection in self.connected_servers.items():
            try:
                # Get real-time system information
                system_info = self._get_system_info(ip, connection['username'], connection.get('password'))
                
                servers_info[ip] = {
                    'name': connection['info'].get('hostname', ip),
                    'ip': ip,
                    'status': 'Online',
                    'ssh_connected': True,
                    'system_info': system_info,
                    'last_check': datetime.now().isoformat()
                }
                
                # Update last check time
                self.connected_servers[ip]['last_check'] = datetime.now().isoformat()
                
            except Exception as e:
                servers_info[ip] = {
                    'name': connection['info'].get('hostname', ip),
                    'ip': ip,
                    'status': 'Error',
                    'ssh_connected': False,
                    'error': str(e),
                    'last_check': datetime.now().isoformat()
                }
        
        return servers_info
    
    def _get_system_info(self, ip: str, username: str, password: str = None) -> dict:
        """Get real-time system information from server"""
        try:
            if password:
                ssh_prefix = f'sshpass -p "{password}" ssh -o StrictHostKeyChecking=no {username}@{ip}'
            else:
                ssh_prefix = f'ssh -o BatchMode=yes {username}@{ip}'
            
            # Get CPU usage
            cpu_cmd = f'{ssh_prefix} "top -bn1 | grep \\"Cpu(s)\\" | awk \\"{{print \\$2}}\\" | cut -d\\"%\\" -f1"'
            cpu_result = subprocess.run(cpu_cmd, shell=True, capture_output=True, text=True, timeout=10)
            cpu_usage = float(cpu_result.stdout.strip()) if cpu_result.stdout.strip() else 0.0
            
            # Get memory usage
            mem_cmd = f'{ssh_prefix} "free -m | grep \\"^Mem:\\" | awk \\"{{print \\$2, \\$3, \\$4, \\$3/\\$2*100}}\\""'
            mem_result = subprocess.run(mem_cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            memory_info = {}
            if mem_result.stdout.strip():
                parts = mem_result.stdout.strip().split()
                memory_info = {
                    'total_mb': int(parts[0]),
                    'used_mb': int(parts[1]),
                    'free_mb': int(parts[2]),
                    'percent': float(parts[3])
                }
            
            # Get disk usage
            disk_cmd = f'{ssh_prefix} "df -h / | tail -1 | awk \\"{{print \\$2, \\$3, \\$4, \\$5}}\\""'
            disk_result = subprocess.run(disk_cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            disk_info = {}
            if disk_result.stdout.strip():
                parts = disk_result.stdout.strip().split()
                disk_info = {
                    'total': parts[0],
                    'used': parts[1],
                    'available': parts[2],
                    'percent': int(parts[3].rstrip('%'))
                }
            
            # Get load average
            load_cmd = f'{ssh_prefix} "cat /proc/loadavg | awk \\"{{print \\$1}}\\""'
            load_result = subprocess.run(load_cmd, shell=True, capture_output=True, text=True, timeout=10)
            load_avg = float(load_result.stdout.strip()) if load_result.stdout.strip() else 0.0
            
            return {
                'cpu_percent': cpu_usage,
                'memory_percent': memory_info.get('percent', 0),
                'disk_percent': disk_info.get('percent', 0),
                'load_avg': load_avg,
                'memory_info': memory_info,
                'disk_info': disk_info
            }
            
        except Exception as e:
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'load_avg': 0,
                'error': str(e)
            }
    
    def save_configuration(self, filename: str = 'server_config.json'):
        """Save server configuration to file"""
        config = {
            'discovered_servers': self.discovered_servers,
            'connected_servers': {ip: {k: v for k, v in info.items() if k != 'password'} 
                                for ip, info in self.connected_servers.items()},
            'network_ranges': self.network_ranges,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2, default=str)
            print(f"✅ Configuration saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            return False
    
    def load_configuration(self, filename: str = 'server_config.json'):
        """Load server configuration from file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                self.discovered_servers = config.get('discovered_servers', {})
                self.connected_servers = config.get('connected_servers', {})
                self.network_ranges = config.get('network_ranges', self.network_ranges)
                
                print(f"✅ Configuration loaded from {filename}")
                return True
            else:
                print(f"📄 No configuration file found: {filename}")
                return False
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            return False
    
    def stop_scanning(self):
        """Stop network scanning"""
        self.scanning = False
        print("🛑 Network scanning stopped")
    
    def get_status_summary(self) -> dict:
        """Get summary of discovery and connection status"""
        return {
            'scanning': self.scanning,
            'discovered_count': len(self.discovered_servers),
            'connected_count': len(self.connected_servers),
            'network_ranges': self.network_ranges,
            'discovered_servers': list(self.discovered_servers.keys()),
            'connected_servers': list(self.connected_servers.keys())
        } 