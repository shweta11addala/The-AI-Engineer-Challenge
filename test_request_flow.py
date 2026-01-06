#!/usr/bin/env python3
"""
Test script to verify the request flow: Frontend -> Backend -> OpenAI
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = "http://localhost:8000"
TEST_MESSAGE = "Hello, this is a test message"

print("=" * 60)
print("Testing Request Flow: Frontend -> Backend -> OpenAI")
print("=" * 60)

# Step 1: Check if backend is running
print("\n1️⃣  Checking if backend is running...")
try:
    response = requests.get(f"{BACKEND_URL}/")
    if response.status_code == 200:
        print(f"   ✅ Backend is running at {BACKEND_URL}")
        print(f"   Response: {response.json()}")
    else:
        print(f"   ❌ Backend returned status {response.status_code}")
        exit(1)
except requests.exceptions.ConnectionError:
    print(f"   ❌ Cannot connect to backend at {BACKEND_URL}")
    print(f"   Make sure the backend is running: uv run uvicorn api.index:app --reload")
    exit(1)

# Step 2: Check API key
print("\n2️⃣  Checking API key configuration...")
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"   ✅ API key found (length: {len(api_key)}, starts with: {api_key[:7]}...)")
else:
    print(f"   ❌ API key NOT found in environment")
    print(f"   Make sure you have a .env file with OPENAI_API_KEY")
    exit(1)

# Step 3: Test the chat endpoint
print(f"\n3️⃣  Testing /api/chat endpoint with message: '{TEST_MESSAGE}'")
try:
    response = requests.post(
        f"{BACKEND_URL}/api/chat",
        json={"message": TEST_MESSAGE},
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ SUCCESS! OpenAI API call worked!")
        print(f"   Response: {data.get('reply', 'No reply field')[:100]}...")
        print(f"\n   🎉 The full flow is working:")
        print(f"      Frontend -> Backend -> OpenAI -> Response")
    else:
        error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
        print(f"   ❌ Request failed")
        print(f"   Error: {error_data}")
        
        if "quota" in str(error_data).lower():
            print(f"\n   ⚠️  This is a QUOTA error from OpenAI")
            print(f"   This means:")
            print(f"   ✅ Frontend successfully called Backend")
            print(f"   ✅ Backend successfully called OpenAI")
            print(f"   ❌ OpenAI rejected due to quota/billing")
            print(f"\n   Check your OpenAI account at:")
            print(f"   https://platform.openai.com/account/billing")
        elif "model" in str(error_data).lower():
            print(f"\n   ⚠️  This might be a MODEL error")
            print(f"   The model 'gpt-5.2' might not be available for your account")
            print(f"   Try changing to 'gpt-3.5-turbo' or 'gpt-4'")
            
except requests.exceptions.Timeout:
    print(f"   ❌ Request timed out (took longer than 30 seconds)")
    print(f"   This might mean OpenAI is not responding")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)

