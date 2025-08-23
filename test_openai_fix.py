#!/usr/bin/env python3
"""
Quick test to verify OpenAI integration is working
"""

import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

def test_openai_new_api():
    """Test OpenAI with new API format"""
    print("🧪 Testing OpenAI New API Format")
    print("=" * 35)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_key or "your_openai" in openai_key:
        print("❌ No valid OpenAI API key found")
        return False
    
    try:
        # Initialize client with new format
        client = openai.OpenAI(api_key=openai_key)
        print("✅ OpenAI client initialized")
        
        # Test simple call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=50,
            messages=[{"role": "user", "content": "Say 'OpenAI integration working!' in exactly 5 words."}]
        )
        
        result = response.choices[0].message.content
        print(f"✅ API Response: {result}")
        
        print("🎉 OpenAI new API format working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

if __name__ == "__main__":
    test_openai_new_api()
#built with love
