#!/usr/bin/env python3
"""
Additional CRUD operations test for StreamManager Pro
"""

import requests
import json
from datetime import datetime, date, timedelta

# Get backend URL
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
        return None

BASE_URL = get_backend_url()
API_URL = f"{BASE_URL}/api"

def test_crud_operations():
    """Test full CRUD operations"""
    print("Testing CRUD Operations...")
    
    # Create a subscriber
    subscriber_data = {
        "service": "HBO MAX",
        "name": "Pedro Sanchez",
        "phone": "573001111111",
        "email": "pedro.sanchez@email.com",
        "expirationDate": (date.today() + timedelta(days=10)).isoformat()
    }
    
    # CREATE
    response = requests.post(f"{API_URL}/subscribers", json=subscriber_data)
    if response.status_code != 200:
        print(f"❌ CREATE failed: {response.status_code}")
        return False
    
    subscriber = response.json()
    subscriber_id = subscriber["id"]
    print(f"✅ CREATE: Subscriber created with ID {subscriber_id}")
    
    # READ (individual)
    response = requests.get(f"{API_URL}/subscribers/{subscriber_id}")
    if response.status_code != 200:
        print(f"❌ READ failed: {response.status_code}")
        return False
    
    retrieved_subscriber = response.json()
    print(f"✅ READ: Retrieved subscriber {retrieved_subscriber['name']}")
    
    # UPDATE
    update_data = {
        "name": "Pedro Sanchez Updated",
        "expirationDate": (date.today() + timedelta(days=20)).isoformat()
    }
    
    response = requests.put(f"{API_URL}/subscribers/{subscriber_id}", json=update_data)
    if response.status_code != 200:
        print(f"❌ UPDATE failed: {response.status_code}")
        return False
    
    updated_subscriber = response.json()
    print(f"✅ UPDATE: Updated subscriber name to {updated_subscriber['name']}")
    
    # DELETE
    response = requests.delete(f"{API_URL}/subscribers/{subscriber_id}")
    if response.status_code != 200:
        print(f"❌ DELETE failed: {response.status_code}")
        return False
    
    print(f"✅ DELETE: Subscriber deleted successfully")
    
    # Verify deletion
    response = requests.get(f"{API_URL}/subscribers/{subscriber_id}")
    if response.status_code == 404:
        print(f"✅ VERIFY DELETE: Subscriber no longer exists")
        return True
    else:
        print(f"❌ VERIFY DELETE failed: Subscriber still exists")
        return False

if __name__ == "__main__":
    success = test_crud_operations()
    if success:
        print("🎉 All CRUD operations working correctly!")
    else:
        print("⚠️ Some CRUD operations failed!")