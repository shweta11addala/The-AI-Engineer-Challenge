#!/usr/bin/env python3
"""
Detailed error testing to see exactly what OpenAI is returning
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ OPENAI_API_KEY not found")
    exit(1)

print("=" * 60)
print("Detailed OpenAI API Error Analysis")
print("=" * 60)
print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
print(f"Key Length: {len(api_key)}")
print()

client = OpenAI(api_key=api_key)

# Test 1: Try to list models (this doesn't use quota)
print("1️⃣  Testing API key validity by listing models...")
try:
    models = client.models.list()
    print(f"   ✅ API key is valid! Can list models.")
    print(f"   Found {len(list(models.data))} models")
except Exception as e:
    print(f"   ❌ Error listing models: {e}")
    print(f"   This might indicate an invalid API key")

print()

# Test 2: Try a simple chat completion
print("2️⃣  Testing chat completion with gpt-3.5-turbo...")
try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Say 'test' if you can read this."}
        ],
        max_tokens=10
    )
    print(f"   ✅ SUCCESS! API call worked!")
    print(f"   Response: {response.choices[0].message.content}")
    print(f"   Usage: {response.usage}")
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}")
    print(f"   Error message: {str(e)}")
    
    # Try to extract more details
    error_str = str(e)
    print()
    print("   Error Analysis:")
    
    if "insufficient_quota" in error_str or "quota" in error_str.lower():
        print("   - Type: QUOTA/Billing Issue")
        print("   - This usually means:")
        print("     • Account has $0 credits")
        print("     • No payment method on file")
        print("     • Free trial expired")
        print("     • Account needs to be upgraded")
    elif "401" in error_str or "unauthorized" in error_str:
        print("   - Type: Authentication Issue")
        print("   - API key might be invalid or revoked")
    elif "model" in error_str.lower() and ("not found" in error_str.lower() or "does not exist" in error_str.lower()):
        print("   - Type: Model Not Available")
        print("   - The model might not be available for your account")
    elif "rate_limit" in error_str.lower() or "429" in error_str:
        print("   - Type: Rate Limit")
        print("   - Too many requests")
    else:
        print(f"   - Type: Unknown - {error_str[:200]}")

print()
print("=" * 60)
print("Recommendations:")
print("=" * 60)
print("1. Check your OpenAI account at: https://platform.openai.com/account/billing")
print("2. Verify you have credits available")
print("3. Check if you need to add a payment method")
print("4. Verify your account status is 'Active'")
print("5. Check if your API key is active at: https://platform.openai.com/api-keys")

