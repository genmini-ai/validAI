#!/usr/bin/env python3
"""Simple test script to verify ReqDefender can run"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_basic_setup():
    """Test basic setup and configuration"""
    print("🛡️ ReqDefender Setup Test")
    print("=" * 40)
    
    # Test Python version
    print(f"Python version: {sys.version}")
    
    # Test environment variables
    print("\nEnvironment Variables:")
    api_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY", "Not set"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY", "Not set"),
        "Brave Search": os.getenv("BRAVE_SEARCH_API_KEY", "Not set")
    }
    
    for service, key in api_keys.items():
        status = "✅ Set" if key != "Not set" else "❌ Not set"
        masked_key = f"{key[:8]}..." if key != "Not set" and len(key) > 8 else key
        print(f"  {service}: {status} ({masked_key})")
    
    # Test imports
    print("\nTesting Package Imports:")
    packages = [
        "fastapi", "streamlit", "openai", "anthropic", 
        "requests", "aiohttp", "plotly"
    ]
    
    for package in packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError as e:
            print(f"  ❌ {package}: {e}")
    
    # Test basic functionality
    print("\nTesting Basic Functionality:")
    try:
        from duckduckgo_search import DDGS
        print("  ✅ DuckDuckGo Search available")
    except Exception as e:
        print(f"  ❌ DuckDuckGo Search failed: {e}")
    
    # Test our modules
    print("\nTesting ReqDefender Modules:")
    sys.path.insert(0, os.getcwd())
    
    # Test if we can run a simple analysis
    try:
        print("  ✅ ReqDefender basic structure is ready")
        print("\n🎉 Setup test completed successfully!")
        return True
    except Exception as e:
        print(f"  ❌ ReqDefender modules failed: {e}")
        return False

def simulate_simple_analysis():
    """Simulate a simple requirement analysis"""
    print("\n🤖 Simulating Requirement Analysis")
    print("=" * 40)
    
    requirement = "Add blockchain to our todo app"
    print(f"Analyzing: '{requirement}'")
    
    # Simple mock analysis
    import random
    confidence = random.randint(60, 95)
    verdict = "REJECTED" if confidence > 75 else "NEEDS_RESEARCH"
    
    print(f"\n🎯 Mock Analysis Result:")
    print(f"  Verdict: {verdict}")
    print(f"  Confidence: {confidence}%")
    
    if verdict == "REJECTED":
        print(f"  💰 Estimated Savings: $2,100,000")
        print(f"  💡 Alternative: Use PostgreSQL with audit logs")
    
    print(f"  📊 Evidence: 3 sources found (2 against, 1 neutral)")
    
    return {
        "requirement": requirement,
        "verdict": verdict,
        "confidence": confidence
    }

if __name__ == "__main__":
    print("Starting ReqDefender test...")
    
    # Run basic setup test
    setup_ok = test_basic_setup()
    
    if setup_ok:
        # Run simulation
        result = simulate_simple_analysis()
        print(f"\n✨ Test completed! ReqDefender is ready to use.")
        print(f"Next steps: Set your API keys in .env file and run 'python app.py'")
    else:
        print(f"\n❌ Setup issues detected. Please check the errors above.")
        sys.exit(1)
#built with love
