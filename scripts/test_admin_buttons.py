#!/usr/bin/env python3
"""
Test script to verify admin button functionality
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
import requests
import json

def test_admin_buttons():
    """Test admin button functionality"""
    print("🔧 ADMIN BUTTON FUNCTIONALITY TEST")
    print("=" * 50)
    
    app = create_app()
    
    with app.test_client() as client:
        # First, login as admin
        login_response = client.post('/api/admin/login', 
            json={'username': 'admin', 'password': 'secret123'})
        
        if login_response.status_code != 200:
            print("❌ Login failed - cannot test buttons")
            return
        
        print("✅ Admin login successful")
        
        # Test 1: Reset voting endpoint
        print("\n1. Testing Reset Voting...")
        reset_response = client.post('/api/admin/reset-voting')
        if reset_response.status_code == 200:
            data = reset_response.get_json()
            print(f"   ✅ Reset voting: {data.get('message', 'Success')}")
        else:
            print(f"   ❌ Reset voting failed: {reset_response.status_code}")
        
        # Test 2: Generate tickets endpoint
        print("\n2. Testing Generate Tickets...")
        generate_response = client.post('/api/admin/generate-tickets', 
            json={'count': 5})
        if generate_response.status_code == 200:
            data = generate_response.get_json()
            print(f"   ✅ Generate tickets: {data.get('message', 'Success')}")
            print(f"   📊 Generated {data.get('count', 0)} tickets")
        else:
            print(f"   ❌ Generate tickets failed: {generate_response.status_code}")
        
        # Test 3: Check ticket stats after generation
        print("\n3. Testing Ticket Stats...")
        stats_response = client.get('/api/ticket/stats')
        if stats_response.status_code == 200:
            data = stats_response.get_json()
            print(f"   ✅ Ticket stats: {data.get('total_tickets', 0)} total tickets")
        else:
            print(f"   ❌ Ticket stats failed: {stats_response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 Admin button functionality test completed!")
    
    print("\n📋 How to test in browser:")
    print("1. Go to: http://localhost:5000/admin-login")
    print("2. Login with: admin / secret123")
    print("3. Click the buttons in the Danger Zone")
    print("4. Check browser console for any errors")

if __name__ == "__main__":
    test_admin_buttons()
