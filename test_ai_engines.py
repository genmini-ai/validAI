#!/usr/bin/env python3
"""
Test which AI engines are being used in the system
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

def test_ai_engine_priority():
    """Test which AI engine has priority in our system"""
    print("🧪 Testing AI Engine Priority in ReqDefender")
    print("=" * 50)
    
    # Test our engine initialization logic
    try:
        import anthropic
        import openai
        
        print("1️⃣ Testing AI Engine Initialization...")
        
        # Check keys
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        print(f"   🔑 Anthropic Key: {'✅ Available' if anthropic_key and 'your_anthropic' not in anthropic_key else '❌ Missing'}")
        print(f"   🔑 OpenAI Key: {'✅ Available' if openai_key and 'your_openai' not in openai_key else '❌ Missing'}")
        
        # Initialize clients like our API does
        anthropic_client = None
        openai_client = None
        
        if anthropic_key and "your_anthropic" not in anthropic_key:
            try:
                anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                print("   🧠 Anthropic Client: ✅ Initialized")
            except Exception as e:
                print(f"   🧠 Anthropic Client: ❌ Error: {e}")
        
        if openai_key and "your_openai" not in openai_key:
            try:
                openai_client = openai.OpenAI(api_key=openai_key)
                print("   🤖 OpenAI Client: ✅ Initialized")
            except Exception as e:
                print(f"   🤖 OpenAI Client: ❌ Error: {e}")
        
        # Test the priority logic from our code
        print(f"\n2️⃣ Testing Engine Selection Logic...")
        
        # This mirrors the logic in our AI methods
        if anthropic_client and openai_client:
            print("   ⚖️ Both engines available")
            print("   🧠 Priority: Anthropic (checked first in if-else chain)")
            print("   🤖 Fallback: OpenAI (used if Anthropic fails)")
            primary_engine = "Anthropic"
            fallback_engine = "OpenAI"
        elif anthropic_client:
            print("   🧠 Only Anthropic available")
            primary_engine = "Anthropic"
            fallback_engine = None
        elif openai_client:
            print("   🤖 Only OpenAI available")
            primary_engine = "OpenAI"
            fallback_engine = None
        else:
            print("   ❌ No AI engines available")
            primary_engine = None
            fallback_engine = None
        
        # Show the actual code pattern
        print(f"\n3️⃣ Code Pattern Analysis...")
        print("   💻 Our AI methods use this pattern:")
        print("   ```python")
        print("   if self.anthropic_client:")
        print("       # Use Anthropic Claude")
        print("   else:")
        print("       # Use OpenAI GPT")
        print("   ```")
        print("   📝 This means Anthropic has priority when both are available")
        
        # Test with a simple call to verify
        print(f"\n4️⃣ Verification Test...")
        
        if anthropic_client:
            try:
                response = anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=30,
                    messages=[{"role": "user", "content": "Say 'Anthropic working' in 3 words"}]
                )
                result = response.content[0].text
                print(f"   🧠 Anthropic Test: ✅ '{result.strip()}'")
            except Exception as e:
                print(f"   🧠 Anthropic Test: ❌ {e}")
        
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    max_tokens=30,
                    messages=[{"role": "user", "content": "Say 'OpenAI working' in 3 words"}]
                )
                result = response.choices[0].message.content
                print(f"   🤖 OpenAI Test: ✅ '{result.strip()}'")
            except Exception as e:
                print(f"   🤖 OpenAI Test: ❌ {e}")
        
        print(f"\n" + "=" * 50)
        print("🎯 AI Engine Configuration Summary:")
        print("=" * 50)
        
        if primary_engine:
            print(f"✅ Primary Engine: {primary_engine}")
            if fallback_engine:
                print(f"🔄 Fallback Engine: {fallback_engine}")
            print(f"🚀 System Status: Dual LLM Setup" if fallback_engine else f"⚡ System Status: Single LLM Setup")
            print(f"💡 Current Behavior: Using {primary_engine} for all AI operations")
            if fallback_engine:
                print(f"🛡️ Redundancy: {fallback_engine} available if {primary_engine} fails")
        else:
            print("❌ System Status: No AI engines available")
            print("🔄 Fallback: Template-based responses only")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    test_ai_engine_priority()
#built with love
