# Server Discovery and Management System

## Overview

The RHEL Resource Manager now includes a dynamic server discovery and management system that allows you to:

1. **Automatically discover servers** in your network
2. **Connect to servers via SSH** directly from the web interface
3. **Monitor multiple servers** simultaneously
4. **Save and load server configurations** for persistence

## Features

### 🔍 Network Discovery
- **Automatic scanning** of network ranges (172.16.16.0/24, 192.168.1.0/24, 10.0.0.0/8)
- **Ping-based detection** of active servers
- **Multi-threaded scanning** for faster discovery
- **Configurable network ranges**

### 🔗 SSH Connection Management
- **Password-based authentication** using sshpass
- **Key-based authentication** for passwordless access
- **Connection testing** before establishing monitoring
- **Automatic reconnection** capabilities

### 📊 Multi-Server Monitoring
- **Real-time system metrics** from all connected servers
- **Unified dashboard** showing all servers
- **Server switching** via dropdown menu
- **Status indicators** for each server

### 💾 Configuration Persistence
- **Save server configurations** to JSON files
- **Load saved configurations** on startup
- **Automatic configuration loading** when dashboard starts

## Usage

### Starting the Dashboard

```bash
# Start the web dashboard
python3 web_dashboard.py

# Or use the main script
python3 main.py --web-dashboard
```

### Using the Settings Interface

1. **Open the dashboard** in your browser (http://localhost:8005)
2. **Click the ⚙️ Settings button** in the top-right corner
3. **Use the Network Discovery section** to scan for servers
4. **Connect to discovered servers** using SSH credentials
5. **Monitor all connected servers** from the main dashboard

### Network Discovery

1. Click **"🔍 Scan Network"** to start discovery
2. Wait for the scan to complete
3. Review discovered servers in the list
4. Click **"🔗 Connect"** on any server you want to monitor

### Adding Servers Manually

1. Enter the **server IP address**
2. Enter the **username** (default: root)
3. Enter the **password** (leave empty for key authentication)
4. Click **"➕ Add Server"**

### Server Management

- **Connected servers** appear in the "Server Connections" section
- **Click "❌ Disconnect"** to remove a server from monitoring
- **Server information** shows hostname, OS, and connection details
- **Status indicators** show if servers are online/offline

## API Endpoints

The system provides REST API endpoints for programmatic access:

### GET Endpoints
- `/api/server-status` - Get current server discovery status

### POST Endpoints
- `/api/scan-network` - Start network scanning
- `/api/stop-scan` - Stop network scanning
- `/api/connect-server` - Connect to a server
- `/api/disconnect-server` - Disconnect from a server
- `/api/save-config` - Save server configuration
- `/api/load-config` - Load server configuration

## Configuration

### Network Ranges
Default network ranges to scan:
- `172.16.16.0/24` - Local development network
- `192.168.1.0/24` - Common home/office network
- `10.0.0.0/8` - Large private network

### SSH Configuration
- **Username**: Default is 'root'
- **Authentication**: Supports both password and key-based auth
- **Timeout**: 5 seconds for connection attempts
- **Key location**: `~/.ssh/id_rsa` (standard SSH key location)

## Testing

Run the test script to verify functionality:

```bash
python3 test_server_discovery.py
```

This will:
- Test module import
- Test configuration save/load
- Test network scanning
- Test SSH connectivity

## Requirements

### System Requirements
- Python 3.12+
- Network access to target servers
- SSH client installed
- `sshpass` for password authentication (optional)

### Python Dependencies
- `psutil` - System monitoring
- `ipaddress` - Network range handling
- `threading` - Multi-threaded scanning
- `subprocess` - SSH command execution

## Security Considerations

1. **SSH Keys**: Use SSH key authentication when possible
2. **Passwords**: Passwords are stored in memory only (not saved to disk)
3. **Network Access**: Ensure proper firewall rules for network scanning
4. **User Permissions**: Run with appropriate user permissions

## Troubleshooting

### Common Issues

1. **"Server discovery not available"**
   - Check that the `core.server_discovery` module is accessible
   - Verify Python path includes the project directory

2. **"SSH connection failed"**
   - Verify SSH is installed and working
   - Check network connectivity to target server
   - Ensure SSH keys are properly configured

3. **"Network scan not finding servers"**
   - Check firewall settings
   - Verify network range is correct
   - Ensure servers are responding to ping

4. **"sshpass not found"**
   - Install sshpass: `sudo yum install sshpass` (RHEL/CentOS)
   - Or use key-based authentication instead

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## File Structure

```
manager_lev1/
├── core/
│   └── server_discovery.py      # Server discovery module
├── web_dashboard.py             # Updated web dashboard
├── test_server_discovery.py     # Test script
└── server_config.json          # Saved server configurations
```

## Future Enhancements

- **SSH key management** interface
- **Custom network ranges** configuration
- **Server grouping** and organization
- **Advanced monitoring** features
- **Alert system** for server status changes
- **Backup and restore** of configurations 