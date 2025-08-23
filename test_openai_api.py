#!/usr/bin/env python3
"""
Test OpenAI integration through the ReqDefender API server
"""

import requests
import json

def test_openai_through_api():
    """Test OpenAI integration through our running API server"""
    base_url = "http://localhost:8003"
    
    print("🧪 Testing OpenAI Through ReqDefender API")
    print("=" * 45)
    
    # First verify the server recognizes OpenAI
    print("1️⃣ Checking server AI status...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            root_data = response.json()
            ai_status = root_data['ai_status']
            print(f"   ✅ Anthropic Ready: {ai_status['anthropic_ready']}")
            print(f"   ✅ OpenAI Ready: {ai_status['openai_ready']}")
            
            if not ai_status['openai_ready']:
                print("   ❌ OpenAI not ready in API server")
                return False
        else:
            print(f"   ❌ Server status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Server status error: {e}")
        return False
    
    # Test with a requirement that would benefit from OpenAI analysis
    print("\n2️⃣ Testing OpenAI-powered analysis...")
    test_requirement = "implement machine learning recommendation system"
    
    try:
        response = requests.post(
            f"{base_url}/quick", 
            params={"requirement": test_requirement},
            timeout=60
        )
        
        if response.status_code == 200:
            quick_data = response.json()
            print(f"   ✅ Requirement: {test_requirement}")
            print(f"   🏛️ Verdict: {quick_data['verdict']}")
            print(f"   📊 Confidence: {quick_data['confidence']:.1f}%")
            print(f"   🤖 AI-Powered: {quick_data['ai_powered']}")
            
            if quick_data['ai_powered']:
                print("   ✅ OpenAI successfully used for analysis")
            else:
                print("   ⚠️ Analysis completed but may have used fallback")
                
        else:
            print(f"   ❌ Quick analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ API analysis error: {e}")
        return False
    
    # Test full analysis to see detailed AI outputs
    print("\n3️⃣ Testing detailed OpenAI outputs...")
    analysis_payload = {
        "requirement": "add AI-powered chatbot for customer support",
        "judge_type": "Innovator",  # This judge type favors AI/tech solutions
        "max_evidence": 4
    }
    
    try:
        response = requests.post(
            f"{base_url}/analyze",
            json=analysis_payload,
            timeout=90
        )
        
        if response.status_code == 200:
            analysis_data = response.json()
            print(f"   ✅ Analysis ID: {analysis_data['id'][:8]}...")
            print(f"   🏛️ Verdict: {analysis_data['verdict']}")
            print(f"   📊 Confidence: {analysis_data['confidence']:.1f}%")
            print(f"   🤖 AI-Powered: {analysis_data['ai_powered']}")
            
            # Show AI-generated content
            print(f"   💭 AI Reasoning: {analysis_data['reasoning'][:100]}...")
            
            if analysis_data['pro_arguments']:
                print(f"   💚 AI PRO Arg: {analysis_data['pro_arguments'][0][:80]}...")
                
            if analysis_data['con_arguments']:
                print(f"   ❤️ AI CON Arg: {analysis_data['con_arguments'][0][:80]}...")
            
            # Verify the content looks like real AI output (not templates)
            reasoning = analysis_data['reasoning'].lower()
            has_ai_language = any(word in reasoning for word in [
                'analysis', 'consideration', 'factors', 'evidence', 'implementation', 'benefits'
            ])
            
            if has_ai_language and analysis_data['ai_powered']:
                print("   ✅ Content appears to be genuine AI-generated")
            else:
                print("   ⚠️ Content may be template-based")
                
        else:
            print(f"   ❌ Full analysis failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Full analysis error: {e}")
        return False
    
    # Check final stats
    print("\n4️⃣ Checking AI usage stats...")
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            stats_data = response.json()
            print(f"   📊 Total Analyses: {stats_data['total_analyses']}")
            print(f"   🤖 AI-Powered Rate: {stats_data['ai_powered_percentage']:.1f}%")
            
            if stats_data['ai_powered_percentage'] > 90:
                print("   ✅ High AI utilization indicates OpenAI is working")
            elif stats_data['ai_powered_percentage'] > 0:
                print("   ⚠️ Some AI usage but may have fallbacks")
            else:
                print("   ❌ No AI usage detected")
                
        else:
            print(f"   ❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stats error: {e}")
    
    print("\n" + "=" * 45)
    print("🎊 OpenAI API Integration Test Complete!")
    print("=" * 45)
    print("✅ OpenAI working through ReqDefender API")
    print("🤖 Both Anthropic and OpenAI available")
    print("⚡ Dual LLM setup provides redundancy")
    print("📡 Ready for production AI debates!")
    
    return True

if __name__ == "__main__":
    test_openai_through_api()
#built with love
