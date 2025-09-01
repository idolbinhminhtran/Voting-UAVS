#!/usr/bin/env python3
"""
Test script to verify admin login system
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env file if it exists
env_path = Path('.env')
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

from app import create_app
import hashlib

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def test_admin_login():
    """Test admin login functionality"""
    print("🔐 ADMIN LOGIN SYSTEM TEST")
    print("=" * 40)
    
    app = create_app()
    
    with app.test_client() as client:
        # Test 1: Check admin status (should be unauthenticated)
        response = client.get('/api/admin/status')
        data = response.get_json()
        print(f"1. Initial status: {'✅' if not data['authenticated'] else '❌'} (Not authenticated)")
        
        # Test 2: Try to access protected endpoint without auth
        response = client.get('/api/ticket/stats')
        print(f"2. Access without auth: {'✅' if response.status_code == 401 else '❌'} (401 Unauthorized)")
        
        # Test 3: Login with wrong credentials
        response = client.post('/api/admin/login', 
            json={'username': 'admin', 'password': 'wrongpassword'})
        print(f"3. Wrong credentials: {'✅' if response.status_code == 401 else '❌'} (401 Unauthorized)")
        
        # Test 4: Login with correct credentials
        response = client.post('/api/admin/login', 
            json={'username': 'admin', 'password': 'secret123'})
        print(f"4. Correct credentials: {'✅' if response.status_code == 200 else '❌'} (200 Success)")
        
        # Test 5: Check status after login
        response = client.get('/api/admin/status')
        data = response.get_json()
        print(f"5. Status after login: {'✅' if data['authenticated'] else '❌'} (Authenticated)")
        
        # Test 6: Access protected endpoint with auth
        response = client.get('/api/ticket/stats')
        print(f"6. Access with auth: {'✅' if response.status_code == 200 else '❌'} (200 Success)")
        
        # Test 7: Logout
        response = client.post('/api/admin/logout')
        print(f"7. Logout: {'✅' if response.status_code == 200 else '❌'} (200 Success)")
        
        # Test 8: Check status after logout
        response = client.get('/api/admin/status')
        data = response.get_json()
        print(f"8. Status after logout: {'✅' if not data['authenticated'] else '❌'} (Not authenticated)")
    
    print("\n" + "=" * 40)
    print("🎉 Admin login system test completed!")
    
    print("\n📋 Default Credentials:")
    print("Username: admin")
    print("Password: secret123")
    print(f"Hash: {hash_password('secret123')}")
    
    print("\n🌐 Access URLs:")
    print("- Login page: http://localhost:5000/admin-login")
    print("- Admin panel: http://localhost:5000/admin")

if __name__ == "__main__":
    test_admin_login()
