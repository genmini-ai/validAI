#!/usr/bin/env python3
"""Quick production test with ONE simple requirement to verify API integration"""

import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

def test_single_api_call():
    """Test ONE real API call with minimal cost"""
    print("🧪 Testing Single API Call (Production Mode)")
    print("-" * 45)
    
    try:
        # Test OpenAI first (usually faster)
        if os.getenv("OPENAI_API_KEY"):
            print("Testing OpenAI with minimal prompt...")
            import openai
            
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Cheapest model
                messages=[{
                    "role": "system", 
                    "content": "You are a product analyst. Be concise."
                }, {
                    "role": "user", 
                    "content": "Is 'add search functionality' a good feature? One sentence."
                }],
                max_tokens=30,  # Limit cost
                temperature=0.7
            )
            
            print(f"✅ OpenAI Response: {response.choices[0].message.content}")
            print(f"💰 Tokens used: ~{response.usage.total_tokens}")
            return True
            
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        
        # Try Anthropic as backup
        try:
            if os.getenv("ANTHROPIC_API_KEY"):
                print("Testing Anthropic...")
                import anthropic
                
                client = anthropic.Anthropic()
                response = client.messages.create(
                    model="claude-3-haiku-20240307",  # Cheapest Claude model
                    max_tokens=30,
                    messages=[{
                        "role": "user",
                        "content": "Is 'add search functionality' a good feature? One sentence."
                    }]
                )
                
                print(f"✅ Anthropic Response: {response.content[0].text}")
                return True
                
        except Exception as e2:
            print(f"❌ Anthropic test failed: {e2}")
            return False
    
    return False

def main():
    print("🛡️ ReqDefender Production Test")
    print("=" * 35)
    print("Testing with ONE simple API call first...")
    print()
    
    if test_single_api_call():
        print("\n✅ SUCCESS! API integration working!")
        print("\n🎯 Next Steps:")
        print("1. Run web interface: python launcher.py web")
        print("2. Test with simple requirement: 'Add search functionality'")
        print("3. Use 'Quick' mode to minimize API usage")
        print("4. Monitor costs in your API provider dashboard")
        print("\n💡 Start with simple requirements before testing complex ones!")
    else:
        print("\n❌ API integration failed. Check your API keys in .env file")

if __name__ == "__main__":
    main()
#built with love
