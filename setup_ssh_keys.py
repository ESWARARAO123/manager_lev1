#!/usr/bin/env python3.12
"""
SSH Key Setup for Remote Server Access
Helps set up passwordless SSH access to 172.16.16.23
"""

import subprocess
import os
import sys
from pathlib import Path

def check_ssh_key_exists():
    """Check if SSH key already exists"""
    ssh_dir = Path.home() / '.ssh'
    private_key = ssh_dir / 'id_rsa'
    public_key = ssh_dir / 'id_rsa.pub'
    
    if private_key.exists() and public_key.exists():
        print("✅ SSH key pair already exists")
        return True
    else:
        print("❌ SSH key pair not found")
        return False

def generate_ssh_key():
    """Generate SSH key pair"""
    print("🔑 Generating SSH key pair...")
    try:
        subprocess.run([
            'ssh-keygen', '-t', 'rsa', '-b', '4096', 
            '-f', str(Path.home() / '.ssh' / 'id_rsa'),
            '-N', ''  # Empty passphrase
        ], check=True)
        print("✅ SSH key pair generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating SSH key: {e}")
        return False

def copy_ssh_key_to_remote():
    """Copy SSH public key to remote server"""
    print("📤 Copying SSH public key to remote server...")
    print("You will be prompted for the remote server password")
    
    try:
        result = subprocess.run([
            'ssh-copy-id', 'root@172.16.16.23'
        ], check=True)
        print("✅ SSH key copied to remote server successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error copying SSH key: {e}")
        print("💡 You can manually copy the key:")
        print("   ssh-copy-id root@172.16.16.23")
        return False

def test_ssh_connection():
    """Test SSH connection to remote server"""
    print("🔍 Testing SSH connection...")
    try:
        result = subprocess.run([
            'ssh', '-o', 'ConnectTimeout=5', 
            '-o', 'BatchMode=yes', 'root@172.16.16.23',
            'echo "SSH connection successful"'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ SSH connection successful (passwordless)")
            return True
        else:
            print("❌ SSH connection failed")
            return False
    except Exception as e:
        print(f"❌ SSH connection error: {e}")
        return False

def get_public_key():
    """Display the public key for manual copying"""
    public_key_path = Path.home() / '.ssh' / 'id_rsa.pub'
    if public_key_path.exists():
        with open(public_key_path, 'r') as f:
            public_key = f.read().strip()
        print("\n📋 Your public SSH key:")
        print("=" * 50)
        print(public_key)
        print("=" * 50)
        print("\n💡 To manually add this key to the remote server:")
        print("1. SSH to the remote server: ssh root@172.16.16.23")
        print("2. Add the key to ~/.ssh/authorized_keys")
        print("3. Set proper permissions: chmod 600 ~/.ssh/authorized_keys")
        return public_key
    else:
        print("❌ Public key not found")
        return None

def main():
    """Main setup function"""
    print("🚀 SSH Key Setup for Remote Server Access")
    print("=" * 50)
    print("This will help you set up passwordless SSH access to 172.16.16.23")
    print()
    
    # Check if SSH key exists
    if not check_ssh_key_exists():
        print("\n🔑 Generating new SSH key pair...")
        if not generate_ssh_key():
            print("❌ Failed to generate SSH key")
            return
    
    # Test current connection
    print("\n🔍 Testing current SSH connection...")
    if test_ssh_connection():
        print("✅ Passwordless SSH is already working!")
        return
    
    # Try to copy SSH key
    print("\n📤 Setting up passwordless SSH...")
    if copy_ssh_key_to_remote():
        # Test again
        if test_ssh_connection():
            print("✅ SSH setup completed successfully!")
            print("🎉 You can now use the web dashboard without password prompts")
            return
    
    # Manual setup instructions
    print("\n📋 Manual Setup Required")
    print("=" * 30)
    print("Since automatic setup failed, here's how to do it manually:")
    print()
    
    public_key = get_public_key()
    
    print("\n🔧 Manual Steps:")
    print("1. Connect to remote server:")
    print("   ssh root@172.16.16.23")
    print()
    print("2. Create .ssh directory (if it doesn't exist):")
    print("   mkdir -p ~/.ssh")
    print("   chmod 700 ~/.ssh")
    print()
    print("3. Add your public key to authorized_keys:")
    print("   echo 'YOUR_PUBLIC_KEY_HERE' >> ~/.ssh/authorized_keys")
    print()
    print("4. Set proper permissions:")
    print("   chmod 600 ~/.ssh/authorized_keys")
    print()
    print("5. Test the connection:")
    print("   ssh root@172.16.16.23")
    print()
    print("💡 After setup, restart the web dashboard to see remote server data")

if __name__ == "__main__":
    main() 