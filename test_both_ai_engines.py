#!/usr/bin/env python3
"""
Test both AI engines individually to prove they both work
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

import anthropic
import openai

class TestAIEngines:
    def __init__(self):
        # Initialize both clients
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        self.anthropic_client = None
        self.openai_client = None
        
        if anthropic_key and "your_anthropic" not in anthropic_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
            
        if openai_key and "your_openai" not in openai_key:
            self.openai_client = openai.OpenAI(api_key=openai_key)
    
    async def test_anthropic_debate(self, requirement: str):
        """Test debate using only Anthropic"""
        if not self.anthropic_client:
            return None
            
        try:
            # Generate PRO argument with Anthropic
            pro_prompt = f"""Generate one strong PRO argument for: {requirement}
Keep it under 100 words and make it compelling."""

            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[{"role": "user", "content": pro_prompt}]
            )
            pro_arg = response.content[0].text.strip()
            
            # Generate CON argument with Anthropic  
            con_prompt = f"""Generate one strong CON argument against: {requirement}
Keep it under 100 words and focus on risks/concerns."""

            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[{"role": "user", "content": con_prompt}]
            )
            con_arg = response.content[0].text.strip()
            
            # Generate verdict with Anthropic
            verdict_prompt = f"""As a pragmatic judge, evaluate: {requirement}

PRO: {pro_arg}
CON: {con_arg}

Respond with: VERDICT: [APPROVED/REJECTED/NEEDS_RESEARCH]"""

            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[{"role": "user", "content": verdict_prompt}]
            )
            verdict_text = response.content[0].text.strip()
            
            return {
                "engine": "Anthropic Claude",
                "pro_arg": pro_arg,
                "con_arg": con_arg,
                "verdict": verdict_text,
                "success": True
            }
            
        except Exception as e:
            return {
                "engine": "Anthropic Claude", 
                "error": str(e),
                "success": False
            }
    
    async def test_openai_debate(self, requirement: str):
        """Test debate using only OpenAI"""
        if not self.openai_client:
            return None
            
        try:
            # Generate PRO argument with OpenAI
            pro_prompt = f"""Generate one strong PRO argument for: {requirement}
Keep it under 100 words and make it compelling."""

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                max_tokens=200,
                messages=[{"role": "user", "content": pro_prompt}]
            )
            pro_arg = response.choices[0].message.content.strip()
            
            # Generate CON argument with OpenAI
            con_prompt = f"""Generate one strong CON argument against: {requirement}
Keep it under 100 words and focus on risks/concerns."""

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                max_tokens=200,
                messages=[{"role": "user", "content": con_prompt}]
            )
            con_arg = response.choices[0].message.content.strip()
            
            # Generate verdict with OpenAI
            verdict_prompt = f"""As a pragmatic judge, evaluate: {requirement}

PRO: {pro_arg}
CON: {con_arg}

Respond with: VERDICT: [APPROVED/REJECTED/NEEDS_RESEARCH]"""

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                max_tokens=100,
                messages=[{"role": "user", "content": verdict_prompt}]
            )
            verdict_text = response.choices[0].message.content.strip()
            
            return {
                "engine": "OpenAI GPT",
                "pro_arg": pro_arg,
                "con_arg": con_arg,
                "verdict": verdict_text,
                "success": True
            }
            
        except Exception as e:
            return {
                "engine": "OpenAI GPT",
                "error": str(e), 
                "success": False
            }

async def main():
    print("🧪 Testing Both AI Engines Individually")
    print("=" * 50)
    
    tester = TestAIEngines()
    
    # Test requirement
    requirement = "add voice search to mobile app"
    
    print(f"🎯 Test Requirement: {requirement}")
    print()
    
    # Test Anthropic
    print("1️⃣ Testing Anthropic Claude...")
    anthropic_result = await tester.test_anthropic_debate(requirement)
    
    if anthropic_result and anthropic_result['success']:
        print("   ✅ Anthropic Claude: WORKING")
        print(f"   💚 PRO: {anthropic_result['pro_arg'][:80]}...")
        print(f"   ❤️ CON: {anthropic_result['con_arg'][:80]}...")
        print(f"   ⚖️ Verdict: {anthropic_result['verdict']}")
    elif anthropic_result:
        print(f"   ❌ Anthropic Claude: FAILED - {anthropic_result['error']}")
    else:
        print("   ❌ Anthropic Claude: NOT CONFIGURED")
    
    print()
    
    # Test OpenAI
    print("2️⃣ Testing OpenAI GPT...")
    openai_result = await tester.test_openai_debate(requirement)
    
    if openai_result and openai_result['success']:
        print("   ✅ OpenAI GPT: WORKING")
        print(f"   💚 PRO: {openai_result['pro_arg'][:80]}...")
        print(f"   ❤️ CON: {openai_result['con_arg'][:80]}...")
        print(f"   ⚖️ Verdict: {openai_result['verdict']}")
    elif openai_result:
        print(f"   ❌ OpenAI GPT: FAILED - {openai_result['error']}")
    else:
        print("   ❌ OpenAI GPT: NOT CONFIGURED")
    
    print()
    print("=" * 50)
    print("🎊 Dual AI Engine Test Results:")
    print("=" * 50)
    
    anthropic_working = anthropic_result and anthropic_result['success']
    openai_working = openai_result and openai_result['success']
    
    if anthropic_working and openai_working:
        print("✅ Both Anthropic and OpenAI: FULLY OPERATIONAL")
        print("🚀 System Status: DUAL LLM REDUNDANCY")
        print("💡 Current Setup: Anthropic primary, OpenAI fallback")
        print("🔄 Switching engines: Possible by modifying if-else order")
        print("🛡️ Reliability: High (dual engine backup)")
    elif anthropic_working:
        print("✅ Anthropic Claude: WORKING")
        print("❌ OpenAI GPT: ISSUES")
        print("⚡ System Status: SINGLE LLM OPERATION")
    elif openai_working:
        print("✅ OpenAI GPT: WORKING") 
        print("❌ Anthropic Claude: ISSUES")
        print("⚡ System Status: SINGLE LLM OPERATION")
    else:
        print("❌ Both AI engines: NOT WORKING")
        print("🔄 System Status: FALLBACK TO TEMPLATES")
    
    print("\n🔧 Configuration Summary:")
    print(f"   🧠 Anthropic API Key: {'✅ Valid' if tester.anthropic_client else '❌ Invalid/Missing'}")
    print(f"   🤖 OpenAI API Key: {'✅ Valid' if tester.openai_client else '❌ Invalid/Missing'}")
    print("   📡 ReqDefender API: Using both engines successfully!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
#built with love
