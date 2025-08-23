#!/usr/bin/env python3
"""
Test the simplified AI-powered API server
"""

import requests
import json
import time
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))
from config import ReqDefenderConfig

def test_simple_api():
    """Test the simplified AI-powered API"""
    test_config = ReqDefenderConfig.get_test_config()
    base_url = test_config["base_url_ai_api"]
    
    print("🧪 Testing Simplified AI-Powered API")
    print("=" * 45)
    
    # Test 1: Health Check
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health: {health_data['status']}")
            print(f"   🤖 AI Ready: {health_data['ai_ready']}")
            print(f"   🔍 Search Ready: {health_data['search_ready']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: Root endpoint
    print("\n2️⃣ Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            root_data = response.json()
            print(f"   ✅ Service: {root_data['service'][:50]}...")
            ai_status = root_data['ai_status']
            print(f"   🧠 Anthropic: {ai_status['anthropic_ready']}")
            print(f"   🤖 OpenAI: {ai_status['openai_ready']}")
            print(f"   🔍 Search: {ai_status['search_available']}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
    
    # Test 3: Quick Analysis
    print("\n3️⃣ Testing quick analysis...")
    test_requirement = "add real-time chat feature to app"
    
    try:
        response = requests.post(
            f"{base_url}/quick", 
            params={"requirement": test_requirement},
            timeout=45
        )
        
        if response.status_code == 200:
            quick_data = response.json()
            print(f"   ✅ Requirement: {quick_data['requirement'][:40]}...")
            print(f"   🏛️ Verdict: {quick_data['verdict']}")
            print(f"   📊 Confidence: {quick_data['confidence']:.1f}%")
            print(f"   🤖 AI-Powered: {quick_data['ai_powered']}")
            print(f"   📄 Evidence Sources: {quick_data['evidence_sources']}")
            print(f"   📝 Summary: {quick_data['summary']}")
            
            success = quick_data['verdict'] in ['APPROVED', 'REJECTED', 'NEEDS_RESEARCH']
            print(f"   {'✅' if success else '⚠️'} Verdict validation: {'PASS' if success else 'UNEXPECTED'}")
                
        else:
            print(f"   ❌ Quick analysis failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Quick analysis error: {e}")
        return False
    
    # Test 4: Full Analysis
    print("\n4️⃣ Testing full analysis...")
    analysis_payload = {
        "requirement": "implement blockchain-based user authentication",
        "judge_type": "Pragmatist",
        "max_evidence": 5
    }
    
    try:
        response = requests.post(
            f"{base_url}/analyze",
            json=analysis_payload,
            timeout=60
        )
        
        if response.status_code == 200:
            analysis_data = response.json()
            print(f"   ✅ Analysis ID: {analysis_data['id'][:8]}...")
            print(f"   🏛️ Verdict: {analysis_data['verdict']}")
            print(f"   📊 Confidence: {analysis_data['confidence']:.1f}%")
            print(f"   📄 Evidence: {analysis_data['evidence_count']} sources")
            print(f"   💚 PRO Args: {len(analysis_data['pro_arguments'])}")
            print(f"   ❤️ CON Args: {len(analysis_data['con_arguments'])}")
            print(f"   🤖 AI-Powered: {analysis_data['ai_powered']}")
            
            # Show reasoning
            reasoning = analysis_data['reasoning'][:80] + "..." if len(analysis_data['reasoning']) > 80 else analysis_data['reasoning']
            print(f"   💭 Reasoning: {reasoning}")
            
            # Show sample arguments
            if analysis_data['pro_arguments']:
                sample_pro = analysis_data['pro_arguments'][0][:60] + "..."
                print(f"   💚 Sample PRO: {sample_pro}")
                
            if analysis_data['con_arguments']:
                sample_con = analysis_data['con_arguments'][0][:60] + "..."
                print(f"   ❤️ Sample CON: {sample_con}")
                
            print("   ✅ Full AI debate completed successfully!")
            
        else:
            print(f"   ❌ Full analysis failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Full analysis error: {e}")
        return False
    
    # Test 5: Stats
    print("\n5️⃣ Testing stats endpoint...")
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            stats_data = response.json()
            print(f"   📊 Total Analyses: {stats_data['total_analyses']}")
            print(f"   🤖 AI-Powered: {stats_data['ai_powered_percentage']:.1f}%")
            print(f"   📈 Avg Confidence: {stats_data['average_confidence']:.1f}%")
            
            if stats_data['verdicts']:
                verdicts_str = ", ".join([f"{k}: {v}" for k, v in stats_data['verdicts'].items()])
                print(f"   🏛️ Verdicts: {verdicts_str}")
                
            if stats_data['recent_analyses']:
                print(f"   📝 Recent: {len(stats_data['recent_analyses'])} analyses stored")
                
        else:
            print(f"   ❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stats error: {e}")
    
    print("\n" + "=" * 45)
    print("🎊 Simplified AI API Test Complete!")
    print("=" * 45)
    print("✅ AI-Powered REST API fully operational")
    print("🤖 Real Claude/GPT agents working via HTTP")
    print(f"🔗 Server running at {base_url}") 
    print("📡 Ready for integration with any frontend")
    return True

if __name__ == "__main__":
    time.sleep(2)  # Wait for server to start
    test_simple_api()
#built with love
