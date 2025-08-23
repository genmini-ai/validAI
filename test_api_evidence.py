#!/usr/bin/env python3
"""
Test the API evidence gathering directly
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import exactly what the API imports
try:
    from research.searcher_working import WorkingResearchPipeline
    SEARCH_AVAILABLE = True
    print("✅ Search components imported successfully")
except ImportError as e:
    SEARCH_AVAILABLE = False
    print(f"❌ Search import failed: {e}")

# Import the API engine
from api_ai_simple import SimpleAIDebateEngine

async def test_api_evidence_gathering():
    """Test the API evidence gathering method"""
    print("🔍 Testing API Evidence Gathering")
    print("=" * 40)
    
    print(f"SEARCH_AVAILABLE: {SEARCH_AVAILABLE}")
    
    # Create engine like the API does
    engine = SimpleAIDebateEngine()
    
    requirement = "implement user authentication system"
    print(f"\n📝 Testing requirement: {requirement}")
    
    try:
        # Call the same method the API calls
        evidence = await engine.gather_simple_evidence(requirement, max_sources=3)
        
        print(f"\n📊 Results:")
        print(f"   Evidence count: {len(evidence)}")
        print(f"   Evidence type: {'Real search' if any('PRO:' in e or 'CON:' in e for e in evidence) else 'Mock/fallback'}")
        
        print(f"\n📋 Evidence details:")
        for i, e in enumerate(evidence, 1):
            print(f"   {i}. {e[:100]}...")
            
        # Try to determine if it's using real search
        has_pro_con = any('PRO:' in e or 'CON:' in e for e in evidence)
        has_mock_format = any('Evidence 1:' in e or 'commonly requested' in e for e in evidence)
        
        print(f"\n🔍 Analysis:")
        print(f"   Contains PRO/CON labels: {has_pro_con}")
        print(f"   Contains mock format: {has_mock_format}")
        
        if has_pro_con:
            print("   ✅ Using REAL search results!")
        elif has_mock_format:
            print("   ❌ Using MOCK evidence")
        else:
            print("   ⚠️ Using fallback evidence")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api_evidence_gathering())
#built with love
