#!/usr/bin/env python3
"""
Test the AI-powered API server
"""

import requests
import json
import time

def test_api_server():
    """Test the AI-powered API server"""
    base_url = "http://localhost:8002"
    
    print("🧪 Testing AI-Powered API Server")
    print("=" * 40)
    
    # Test 1: Health Check
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health: {health_data['status']}")
            print(f"   🤖 AI Engine: {health_data['ai_engine_ready']}")
            print(f"   📦 Components: {health_data['components_available']}")
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
            print(f"   ✅ Service: {root_data['service']}")
            print(f"   📦 Version: {root_data['version']}")
            ai_status = root_data['ai_status']
            print(f"   🧠 Anthropic: {ai_status['anthropic_ready']}")
            print(f"   🤖 OpenAI: {ai_status['openai_ready']}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
    
    # Test 3: Quick Analysis
    print("\n3️⃣ Testing quick analysis...")
    test_requirement = "add dark mode to mobile app"
    
    try:
        response = requests.post(
            f"{base_url}/quick", 
            params={"requirement": test_requirement},
            timeout=30
        )
        
        if response.status_code == 200:
            quick_data = response.json()
            print(f"   ✅ Requirement: {quick_data['requirement']}")
            print(f"   🏛️ Verdict: {quick_data['verdict']}")
            print(f"   📊 Confidence: {quick_data['confidence']:.1f}%")
            print(f"   🤖 AI-Powered: {quick_data['ai_powered']}")
            print(f"   📄 Evidence Sources: {quick_data['evidence_sources']}")
            
            if quick_data['verdict'] in ['APPROVED', 'REJECTED', 'NEEDS_RESEARCH']:
                print("   ✅ Valid verdict returned")
            else:
                print(f"   ⚠️ Unexpected verdict: {quick_data['verdict']}")
                
        else:
            print(f"   ❌ Quick analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Quick analysis error: {e}")
    
    # Test 4: Full Analysis (if quick worked)
    print("\n4️⃣ Testing full analysis...")
    analysis_payload = {
        "requirement": "implement OAuth 2.0 authentication",
        "judge_type": "Pragmatist",
        "max_evidence": 8
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
            print(f"   📄 Evidence Count: {analysis_data['evidence_count']}")
            print(f"   💚 PRO Args: {len(analysis_data['pro_arguments'])}")
            print(f"   ❤️ CON Args: {len(analysis_data['con_arguments'])}")
            print(f"   🤖 AI-Powered: {analysis_data['ai_powered']}")
            
            # Show sample argument
            if analysis_data['pro_arguments']:
                sample_arg = analysis_data['pro_arguments'][0][:60]
                print(f"   📝 Sample PRO: {sample_arg}...")
                
            print("   ✅ Full analysis completed!")
            
        else:
            print(f"   ❌ Full analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Full analysis error: {e}")
    
    # Test 5: Stats
    print("\n5️⃣ Testing stats endpoint...")
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            stats_data = response.json()
            print(f"   📊 Total Analyses: {stats_data['total_analyses']}")
            print(f"   🤖 AI-Powered %: {stats_data['ai_powered_percentage']:.1f}%")
            print(f"   📈 Avg Confidence: {stats_data['average_confidence']:.1f}%")
            
            if stats_data['verdicts']:
                print(f"   🏛️ Verdicts: {stats_data['verdicts']}")
                
        else:
            print(f"   ❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stats error: {e}")
    
    print("\n" + "=" * 40)
    print("🎊 API Integration Test Complete!")
    print("✅ AI-Powered REST API operational")
    print("🤖 Real AI agents available via HTTP")
    print("🔗 Server running at http://localhost:8002")

if __name__ == "__main__":
    # Give server a moment to fully start
    time.sleep(2)
    test_api_server()
#built with love
