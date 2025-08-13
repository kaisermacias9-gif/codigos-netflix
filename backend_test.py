#!/usr/bin/env python3
"""
StreamManager Pro Backend API Test Suite
Tests all backend endpoints comprehensively
"""

import requests
import json
from datetime import datetime, date, timedelta
import uuid
import sys
import os

# Get backend URL from frontend .env file
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
if not BASE_URL:
    print("ERROR: Could not get backend URL from frontend/.env")
    sys.exit(1)

API_URL = f"{BASE_URL}/api"
print(f"Testing API at: {API_URL}")

# Test data
test_subscriber_data = {
    "service": "NETFLIX",
    "name": "Maria Rodriguez",
    "phone": "573001234567",
    "email": "maria.rodriguez@email.com",
    "expirationDate": (date.today() + timedelta(days=15)).isoformat()
}

test_subscriber_expiring = {
    "service": "SPOTIFY",
    "name": "Carlos Mendez",
    "phone": "573007654321", 
    "email": "carlos.mendez@email.com",
    "expirationDate": (date.today() + timedelta(days=3)).isoformat()
}

test_subscriber_expired = {
    "service": "DISNEY+",
    "name": "Ana Gutierrez",
    "phone": "573009876543",
    "email": "ana.gutierrez@email.com", 
    "expirationDate": (date.today() - timedelta(days=5)).isoformat()
}

# Global variables to store created subscriber IDs
created_subscriber_ids = []

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")

def print_result(success, message, details=None):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    if details:
        print(f"Details: {details}")

def test_health_check():
    """Test GET /api/ - Health check endpoint"""
    print_test_header("Health Check")
    
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "version" in data:
                print_result(True, f"Health check successful - Status: {response.status_code}")
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print_result(False, "Health check response missing required fields", data)
                return False
        else:
            print_result(False, f"Health check failed - Status: {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Health check request failed: {str(e)}")
        return False

def test_get_services():
    """Test GET /api/services - Get streaming services"""
    print_test_header("Get Services")
    
    try:
        response = requests.get(f"{API_URL}/services", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "services" in data and isinstance(data["services"], list):
                expected_services = ["NETFLIX", "AMAZON PRIME", "DISNEY+", "HBO MAX", "SPOTIFY", "YOUTUBE PREMIUM", "APPLE TV+", "PARAMOUNT+"]
                if len(data["services"]) > 0:
                    print_result(True, f"Services retrieved successfully - Count: {len(data['services'])}")
                    print(f"Services: {data['services']}")
                    return True
                else:
                    print_result(False, "No services returned", data)
                    return False
            else:
                print_result(False, "Invalid services response format", data)
                return False
        else:
            print_result(False, f"Get services failed - Status: {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get services request failed: {str(e)}")
        return False

def test_create_subscriber():
    """Test POST /api/subscribers - Create new subscriber"""
    print_test_header("Create Subscriber")
    
    try:
        # Test creating active subscriber
        response = requests.post(
            f"{API_URL}/subscribers",
            json=test_subscriber_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["id", "name", "service", "phone", "email", "expirationDate", "status", "daysRemaining"]
            
            if all(field in data for field in required_fields):
                created_subscriber_ids.append(data["id"])
                print_result(True, f"Active subscriber created successfully - ID: {data['id']}")
                print(f"Subscriber: {data['name']} - Status: {data['status']} - Days: {data['daysRemaining']}")
                
                # Test creating expiring subscriber
                response2 = requests.post(
                    f"{API_URL}/subscribers",
                    json=test_subscriber_expiring,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    created_subscriber_ids.append(data2["id"])
                    print_result(True, f"Expiring subscriber created - ID: {data2['id']}, Status: {data2['status']}")
                    
                    # Test creating expired subscriber
                    response3 = requests.post(
                        f"{API_URL}/subscribers",
                        json=test_subscriber_expired,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    
                    if response3.status_code == 200:
                        data3 = response3.json()
                        created_subscriber_ids.append(data3["id"])
                        print_result(True, f"Expired subscriber created - ID: {data3['id']}, Status: {data3['status']}")
                        return True
                    else:
                        print_result(False, f"Failed to create expired subscriber - Status: {response3.status_code}", response3.text)
                        return False
                else:
                    print_result(False, f"Failed to create expiring subscriber - Status: {response2.status_code}", response2.text)
                    return False
            else:
                missing_fields = [field for field in required_fields if field not in data]
                print_result(False, f"Response missing required fields: {missing_fields}", data)
                return False
        else:
            print_result(False, f"Create subscriber failed - Status: {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Create subscriber request failed: {str(e)}")
        return False

def test_get_all_subscribers():
    """Test GET /api/subscribers - Get all subscribers"""
    print_test_header("Get All Subscribers")
    
    try:
        response = requests.get(f"{API_URL}/subscribers", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "subscribers" in data and "total" in data:
                subscribers = data["subscribers"]
                total = data["total"]
                
                if len(subscribers) >= 3:  # We created 3 subscribers
                    print_result(True, f"Retrieved {total} subscribers successfully")
                    
                    # Verify different statuses exist
                    statuses = [sub["status"] for sub in subscribers]
                    status_counts = {
                        "active": statuses.count("active"),
                        "expiring": statuses.count("expiring"), 
                        "expired": statuses.count("expired")
                    }
                    print(f"Status distribution: {status_counts}")
                    
                    # Verify required fields in each subscriber
                    required_fields = ["id", "name", "service", "status", "daysRemaining"]
                    for sub in subscribers:
                        if not all(field in sub for field in required_fields):
                            print_result(False, f"Subscriber missing required fields: {sub}")
                            return False
                    
                    return True
                else:
                    print_result(False, f"Expected at least 3 subscribers, got {len(subscribers)}", data)
                    return False
            else:
                print_result(False, "Invalid subscribers response format", data)
                return False
        else:
            print_result(False, f"Get subscribers failed - Status: {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get subscribers request failed: {str(e)}")
        return False

def test_get_stats():
    """Test GET /api/stats - Get dashboard statistics"""
    print_test_header("Get Statistics")
    
    try:
        response = requests.get(f"{API_URL}/stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["total", "active", "expiring", "expired", "revenue"]
            
            if all(field in data for field in required_fields):
                print_result(True, "Statistics retrieved successfully")
                print(f"Stats: Total={data['total']}, Active={data['active']}, Expiring={data['expiring']}, Expired={data['expired']}, Revenue=${data['revenue']}")
                
                # Verify stats make sense
                if data["total"] == data["active"] + data["expiring"] + data["expired"]:
                    print_result(True, "Statistics totals are consistent")
                    
                    # Verify revenue calculation (should be (active + expiring) * 15)
                    expected_revenue = (data["active"] + data["expiring"]) * 15.0
                    if abs(data["revenue"] - expected_revenue) < 0.01:
                        print_result(True, f"Revenue calculation correct: ${data['revenue']}")
                        return True
                    else:
                        print_result(False, f"Revenue calculation incorrect. Expected: ${expected_revenue}, Got: ${data['revenue']}")
                        return False
                else:
                    print_result(False, f"Statistics totals inconsistent: {data}")
                    return False
            else:
                missing_fields = [field for field in required_fields if field not in data]
                print_result(False, f"Stats response missing required fields: {missing_fields}", data)
                return False
        else:
            print_result(False, f"Get stats failed - Status: {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get stats request failed: {str(e)}")
        return False

def test_send_message():
    """Test POST /api/send-message - Send message to subscriber"""
    print_test_header("Send Message")
    
    if not created_subscriber_ids:
        print_result(False, "No subscribers available for message testing")
        return False
    
    try:
        subscriber_id = created_subscriber_ids[0]
        
        # Test reminder message
        message_data = {
            "subscriberId": subscriber_id,
            "messageType": "recordatorio"
        }
        
        response = requests.post(
            f"{API_URL}/send-message",
            json=message_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["success", "message", "messageLog"]
            
            if all(field in data for field in required_fields):
                if data["success"] and data["messageLog"]:
                    print_result(True, f"Reminder message sent successfully")
                    print(f"Message: {data['message']}")
                    
                    # Test expiration message
                    message_data2 = {
                        "subscriberId": subscriber_id,
                        "messageType": "vencimiento"
                    }
                    
                    response2 = requests.post(
                        f"{API_URL}/send-message",
                        json=message_data2,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    
                    if response2.status_code == 200:
                        data2 = response2.json()
                        if data2["success"]:
                            print_result(True, "Expiration message sent successfully")
                            
                            # Test custom message
                            message_data3 = {
                                "subscriberId": subscriber_id,
                                "messageType": "personalizado",
                                "message": "Este es un mensaje personalizado de prueba"
                            }
                            
                            response3 = requests.post(
                                f"{API_URL}/send-message",
                                json=message_data3,
                                headers={"Content-Type": "application/json"},
                                timeout=10
                            )
                            
                            if response3.status_code == 200:
                                data3 = response3.json()
                                if data3["success"]:
                                    print_result(True, "Custom message sent successfully")
                                    return True
                                else:
                                    print_result(False, "Custom message failed", data3)
                                    return False
                            else:
                                print_result(False, f"Custom message request failed - Status: {response3.status_code}", response3.text)
                                return False
                        else:
                            print_result(False, "Expiration message failed", data2)
                            return False
                    else:
                        print_result(False, f"Expiration message request failed - Status: {response2.status_code}", response2.text)
                        return False
                else:
                    print_result(False, "Message sending failed", data)
                    return False
            else:
                missing_fields = [field for field in required_fields if field not in data]
                print_result(False, f"Send message response missing required fields: {missing_fields}", data)
                return False
        else:
            print_result(False, f"Send message failed - Status: {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Send message request failed: {str(e)}")
        return False

def test_error_handling():
    """Test error handling with invalid data"""
    print_test_header("Error Handling")
    
    try:
        # Test invalid subscriber ID for message sending
        invalid_message_data = {
            "subscriberId": "invalid-id-12345",
            "messageType": "recordatorio"
        }
        
        response = requests.post(
            f"{API_URL}/send-message",
            json=invalid_message_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 404:
            print_result(True, "Invalid subscriber ID correctly returns 404")
        else:
            print_result(False, f"Expected 404 for invalid subscriber ID, got {response.status_code}")
            return False
        
        # Test invalid subscriber creation (missing required fields)
        invalid_subscriber = {
            "name": "Test User"
            # Missing required fields
        }
        
        response2 = requests.post(
            f"{API_URL}/subscribers",
            json=invalid_subscriber,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response2.status_code == 422:  # Validation error
            print_result(True, "Invalid subscriber data correctly returns 422")
        else:
            print_result(False, f"Expected 422 for invalid subscriber data, got {response2.status_code}")
            return False
        
        # Test getting non-existent subscriber
        response3 = requests.get(f"{API_URL}/subscribers/non-existent-id", timeout=10)
        
        if response3.status_code == 404:
            print_result(True, "Non-existent subscriber correctly returns 404")
            return True
        else:
            print_result(False, f"Expected 404 for non-existent subscriber, got {response3.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error handling test failed: {str(e)}")
        return False

def cleanup_test_data():
    """Clean up test subscribers"""
    print_test_header("Cleanup Test Data")
    
    deleted_count = 0
    for subscriber_id in created_subscriber_ids:
        try:
            response = requests.delete(f"{API_URL}/subscribers/{subscriber_id}", timeout=10)
            if response.status_code == 200:
                deleted_count += 1
        except Exception as e:
            print(f"Failed to delete subscriber {subscriber_id}: {e}")
    
    print_result(True, f"Cleaned up {deleted_count} test subscribers")

def main():
    """Run all backend tests"""
    print("StreamManager Pro Backend API Test Suite")
    print(f"Testing API at: {API_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    tests = [
        ("Health Check", test_health_check),
        ("Get Services", test_get_services),
        ("Create Subscriber", test_create_subscriber),
        ("Get All Subscribers", test_get_all_subscribers),
        ("Get Statistics", test_get_stats),
        ("Send Message", test_send_message),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_result(False, f"Test {test_name} crashed: {str(e)}")
            results.append((test_name, False))
    
    # Cleanup
    cleanup_test_data()
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Backend API is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)