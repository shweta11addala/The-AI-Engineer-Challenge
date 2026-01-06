#!/usr/bin/env python3
"""
Test script to verify OpenAI API key is loaded correctly and test API access
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

print("=" * 60)
print("OpenAI API Key Verification & Test")
print("=" * 60)

# Check if key exists
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ OPENAI_API_KEY is NOT configured")
    print("\nMake sure you have a .env file with:")
    print("  OPENAI_API_KEY=sk-your-key-here")
    exit(1)

print(f"✅ API Key found")
print(f"   Length: {len(api_key)} characters")
print(f"   Starts with: {api_key[:7]}...")
print(f"   Ends with: ...{api_key[-4:]}\n")

# Validate format
if not api_key.startswith("sk-"):
    print("⚠️  WARNING: Key doesn't start with 'sk-'")
    print("   This might not be a valid OpenAI API key format")
else:
    print("✅ Key format looks correct\n")

# Try to create OpenAI client
try:
    print("Creating OpenAI client...")
    client = OpenAI(api_key=api_key)
    print("✅ Client created successfully\n")
    
    # Try a minimal API call to test the key
    print("Testing API call with a simple request...")
    print("(This will help identify if it's a quota issue or key issue)\n")
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using a cheaper model for testing
            messages=[
                {"role": "user", "content": "Say 'test' if you can read this."}
            ],
            max_tokens=10
        )
        print("✅ API call SUCCESSFUL!")
        print(f"   Response: {response.choices[0].message.content}")
        print("\n✅ Your API key is valid and working!")
        print("   If you're getting quota errors with gpt-5, try:")
        print("   - Check if gpt-5 model is available in your account")
        print("   - Try using 'gpt-4' or 'gpt-3.5-turbo' instead")
        
    except Exception as api_error:
        error_str = str(api_error)
        print("❌ API call FAILED")
        print(f"\nError details:")
        print(f"   {error_str}\n")
        
        # Parse common errors
        if "insufficient_quota" in error_str or "quota" in error_str.lower():
            print("🔍 DIAGNOSIS: Quota/Billing Issue")
            print("\nThis means:")
            print("  ✅ Your API key is VALID and correctly configured")
            print("  ❌ Your OpenAI account has quota/billing issues")
            print("\nTo fix:")
            print("  1. Go to https://platform.openai.com/account/billing")
            print("  2. Add a payment method if you haven't")
            print("  3. Check your usage limits")
            print("  4. Verify your account has available credits/quota")
            print("  5. If using a free tier, you may need to upgrade")
            
        elif "401" in error_str or "unauthorized" in error_str.lower() or "Invalid API key" in error_str:
            print("🔍 DIAGNOSIS: Invalid API Key")
            print("\nThis means:")
            print("  ❌ The API key is not valid or has been revoked")
            print("\nTo fix:")
            print("  1. Get a new API key from https://platform.openai.com/api-keys")
            print("  2. Make sure you're copying the full key")
            print("  3. Check that the key hasn't been deleted/revoked")
            
        elif "429" in error_str or "rate limit" in error_str.lower():
            print("🔍 DIAGNOSIS: Rate Limit Issue")
            print("\nThis means:")
            print("  ✅ Your API key is valid")
            print("  ⚠️  You're hitting rate limits")
            print("\nTo fix:")
            print("  - Wait a few minutes and try again")
            print("  - Check your rate limits at https://platform.openai.com/account/limits")
            
        elif "model" in error_str.lower() and ("not found" in error_str.lower() or "does not exist" in error_str.lower()):
            print("🔍 DIAGNOSIS: Model Not Available")
            print("\nThis means:")
            print("  ✅ Your API key is valid")
            print("  ❌ The model 'gpt-5' doesn't exist or isn't available")
            print("\nTo fix:")
            print("  - Change the model in api/index.py from 'gpt-5' to:")
            print("    - 'gpt-4' or 'gpt-4-turbo-preview'")
            print("    - 'gpt-3.5-turbo' (cheaper option)")
            
        else:
            print("🔍 DIAGNOSIS: Unknown Error")
            print("\nPlease check the error message above for details")
            
except ImportError:
    print("❌ Could not import OpenAI library")
    print("   Run: uv sync")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)

