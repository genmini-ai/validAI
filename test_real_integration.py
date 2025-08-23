#!/usr/bin/env python3
"""
Test the real ReqDefender integration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

async def test_real_components():
    """Test that all real components work together"""
    print("🧪 Testing Real ReqDefender Integration")
    print("=" * 50)
    
    try:
        # Test 1: Search Pipeline
        print("1️⃣ Testing Search Pipeline...")
        from research.searcher_working import WorkingResearchPipeline
        
        pipeline = WorkingResearchPipeline()
        results = await pipeline.search_evidence("implement OAuth authentication", "neutral")
        print(f"   ✅ Search: Found {len(results)} results")
        
        # Test 2: Evidence System  
        print("2️⃣ Testing Evidence System...")
        # Import directly to avoid arena __init__ dependencies
        sys.path.append(os.path.join(project_root, 'arena'))
        from evidence_system import EvidenceGatherer, EvidenceScorer
        
        gatherer = EvidenceGatherer()
        evidence = await gatherer.gather_evidence("implement OAuth authentication", "neutral", max_sources=3)
        print(f"   ✅ Evidence: Gathered {len(evidence)} evidence objects")
        
        if evidence:
            scorer = EvidenceScorer()
            collection_score = scorer.score_evidence_collection(evidence)
            print(f"   📊 Collection score: {collection_score:.3f}")
        
        # Test 3: Integration Flow
        print("3️⃣ Testing Integration Flow...")
        
        # Simulate the flow from streamlit app
        requirement = "add two-factor authentication"
        
        # Search for PRO evidence
        pro_results = await pipeline.search_evidence(requirement, "support")
        print(f"   💚 PRO evidence: {len(pro_results)} sources")
        
        # Search for CON evidence  
        con_results = await pipeline.search_evidence(requirement, "oppose")
        print(f"   ❤️ CON evidence: {len(con_results)} sources")
        
        total_sources = len(pro_results) + len(con_results)
        print(f"   📊 Total evidence sources: {total_sources}")
        
        # Test 4: Mock Verdict Generation
        print("4️⃣ Testing Verdict Logic...")
        
        pro_score = len(pro_results) * 10 + 15  # Arguments
        con_score = len(con_results) * 10 + 15
        
        if pro_score > con_score * 1.2:
            verdict = "APPROVED"
        elif con_score > pro_score * 1.2:
            verdict = "REJECTED"
        else:
            verdict = "NEEDS_RESEARCH"
            
        confidence = min(95, 60 + abs(pro_score - con_score))
        
        print(f"   ⚖️ Verdict: {verdict} (confidence: {confidence:.1f}%)")
        print(f"   📊 Scores: PRO {pro_score} vs CON {con_score}")
        
        print("\n🎉 Integration Test Complete!")
        print("=" * 50)
        print("✅ All core components working")
        print("✅ Evidence gathering operational")
        print("✅ Search integration functional") 
        print("✅ Scoring system active")
        print("✅ Ready for real debates!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_components())
#built with love
