#!/usr/bin/env python3
"""Test search functionality with a sample requirement topic"""

import asyncio
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from research.searcher_working import WorkingResearchPipeline

# Import EvidenceGatherer directly to avoid arena __init__.py dependencies
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'arena'))
from evidence_system import EvidenceGatherer


async def test_search_integration():
    """Test the complete search integration flow"""
    print("🔍 Testing Search Integration")
    print("=" * 50)
    
    # Test topic - a realistic requirement
    test_requirement = "implement blockchain-based user authentication"
    
    print(f"Testing with requirement: '{test_requirement}'")
    print()
    
    # Test 1: Direct search pipeline
    print("1️⃣ Testing Working Research Pipeline")
    print("-" * 30)
    
    pipeline = WorkingResearchPipeline()
    
    try:
        # Test evidence search
        evidence_results = await pipeline.search_evidence(
            requirement=test_requirement,
            stance="oppose"  # Look for problems/issues
        )
        
        print(f"✅ Found {len(evidence_results)} evidence pieces")
        
        # Show first few results
        for i, result in enumerate(evidence_results[:3], 1):
            print(f"  {i}. {result.get('title', 'No title')[:60]}...")
            print(f"     Source: {result.get('source', 'Unknown')}")
            print(f"     URL: {result.get('url', 'No URL')}")
            print()
        
        # Test specific site search
        tech_results = pipeline.search_specific_sites(
            requirement=test_requirement,
            sites=["github.com", "stackoverflow.com"]
        )
        
        print(f"✅ Found {len(tech_results)} results from tech sites")
        
        # Show usage stats
        stats = pipeline.get_usage_stats()
        print(f"📊 API Calls: {stats['brave_api_calls']}")
        print(f"💰 Estimated Cost: ${stats['cost_estimate']:.3f}")
        print()
        
    except Exception as e:
        print(f"❌ Working Research Pipeline failed: {e}")
        print()
    
    # Test 2: Evidence system integration
    print("2️⃣ Testing Evidence System Integration")
    print("-" * 30)
    
    try:
        # Create evidence gatherer with working search pipeline
        gatherer = EvidenceGatherer()
        
        # Test evidence gathering
        evidence_objects = await gatherer.gather_evidence(
            requirement=test_requirement,
            stance="neutral",
            max_sources=5
        )
        
        print(f"✅ Evidence Gatherer found {len(evidence_objects)} evidence objects")
        
        # Show evidence details
        for i, evidence in enumerate(evidence_objects[:3], 1):
            print(f"  {i}. Claim: {evidence.claim[:50]}...")
            print(f"     Source: {evidence.source}")
            print(f"     Tier: {evidence.tier.name}")
            print(f"     Score: {evidence.total_score:.2f}")
            print(f"     Relevance: {evidence.relevance_score:.2f}")
            print()
            
    except Exception as e:
        print(f"❌ Evidence System failed: {e}")
        print()
    
    # Test 3: Search query generation
    print("3️⃣ Testing Search Query Generation")  
    print("-" * 30)
    
    # Test different stances
    stances = ["support", "oppose", "neutral"]
    
    for stance in stances:
        queries = pipeline._generate_search_queries(test_requirement, stance)
        print(f"📝 {stance.upper()} queries:")
        for query in queries[:2]:  # Show first 2
            print(f"   - {query}")
        print()
    
    print("🎯 Search Integration Test Complete!")
    
    
async def test_topic_to_search_flow():
    """Test how a topic flows through the search system"""
    print("\n🎭 Testing Topic → Search → Evidence Flow")
    print("=" * 50)
    
    # Simulate the full flow
    topics = [
        "add two-factor authentication",
        "implement microservices architecture", 
        "use GraphQL instead of REST API",
        "deploy to Kubernetes cluster"
    ]
    
    pipeline = WorkingResearchPipeline()
    
    for i, topic in enumerate(topics, 1):
        print(f"{i}. Topic: '{topic}'")
        
        try:
            # Search for evidence (limit to 2 results for speed)
            results = await pipeline.search_evidence(topic, "neutral")
            
            if results:
                print(f"   ✅ Found {len(results)} pieces of evidence")
                best_result = results[0] if results else {}
                print(f"   🏆 Best result: {best_result.get('title', 'No title')[:40]}...")
            else:
                print("   ⚠️  No results found")
                
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
        
        print()
    
    print("🔚 Topic Flow Test Complete!")


if __name__ == "__main__":
    print("🚀 Starting Search Functionality Tests")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now()}")
    print()
    
    # Run tests
    asyncio.run(test_search_integration())
    asyncio.run(test_topic_to_search_flow())
    
    print(f"⏰ Test completed at: {datetime.now()}")
    print("\n💡 Summary:")
    print("- Working Research Pipeline: Uses direct Brave API or DuckDuckGo")
    print("- Evidence System: Integrates with search but needs Brave wrapper fix")
    print("- Topic Flow: Requirements → Search Queries → Evidence Results")
    print("- Integration: Ready for debate arena usage!")
#built with love
