#!/usr/bin/env python3
"""
Test script to verify FastAPI server is running and responding correctly
"""

import requests
import json
import time

def test_server():
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing FastAPI Server Connection...")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Try running: python run_server.py")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Chat endpoint
    try:
        print("\n2. Testing chat endpoint...")
        chat_data = {
            "message": "I have fever and cough",
            "user_id": 1
        }
        response = requests.post(f"{base_url}/chat", json=chat_data, timeout=10)
        if response.status_code == 200:
            print("✅ Chat endpoint working")
            result = response.json()
            print(f"   Response: {result['response'][:100]}...")
            print(f"   Consultation ID: {result.get('consultation_id', 'None')}")
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Chat test error: {e}")
    
    # Test 3: List consultations
    try:
        print("\n3. Testing consultations list...")
        response = requests.get(f"{base_url}/_list_recent", timeout=5)
        if response.status_code == 200:
            print("✅ Consultations endpoint working")
            consultations = response.json()
            print(f"   Found {len(consultations)} consultations")
        else:
            print(f"❌ Consultations endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Consultations test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Server test completed!")
    print("\nIf all tests passed, your chatbot should work now.")
    print("Open: http://127.0.0.1:5000/static/chatbot-demo.html")
    
    return True

if __name__ == "__main__":
    test_server()
