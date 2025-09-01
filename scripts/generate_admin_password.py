#!/usr/bin/env python3
"""
Script to generate admin password hash
"""

import hashlib
import sys

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/generate_admin_password.py <password>")
        print("Example: python scripts/generate_admin_password.py mypassword123")
        sys.exit(1)
    
    password = sys.argv[1]
    hashed = hash_password(password)
    
    print("🔐 Admin Password Hash Generator")
    print("=" * 40)
    print(f"Password: {password}")
    print(f"Hash: {hashed}")
    print()
    print("Add these to your Railway environment variables:")
    print(f"ADMIN_USERNAME=admin")
    print(f"ADMIN_PASSWORD_HASH={hashed}")
    print()
    print("Default credentials (for testing):")
    print("Username: admin")
    print("Password: secret123")
    print("Hash: ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f")

if __name__ == "__main__":
    main()
