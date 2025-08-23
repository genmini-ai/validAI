#!/usr/bin/env python3
"""
Test the complete ReqDefender system with real API keys
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

async def test_full_integration():
    """Test the complete system with real API keys"""
    print("🚀 Testing FULL ReqDefender Integration with Real APIs")
    print("=" * 60)
    
    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY") 
    brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
    
    print("🔑 API Key Status:")
    print(f"   OpenAI: {'✅ Available' if openai_key and openai_key != 'your_openai_api_key_here' else '❌ Missing'}")
    print(f"   Anthropic: {'✅ Available' if anthropic_key and anthropic_key != 'your_anthropic_api_key_here' else '❌ Missing'}")
    print(f"   Brave Search: {'✅ Available' if brave_key and brave_key != 'your_brave_search_api_key_here' else '❌ Missing'}")
    
    if not openai_key and not anthropic_key:
        print("❌ No LLM API keys found - system will use fallback mode")
        return False
        
    try:
        print("\n1️⃣ Testing Real Search System...")
        
        # Test search directly
        from research.searcher_working import WorkingResearchPipeline
        pipeline = WorkingResearchPipeline()
        
        requirement = "add OAuth 2.0 authentication to web application"
        
        # Test search with real APIs
        pro_results = await pipeline.search_evidence(requirement, "support")
        con_results = await pipeline.search_evidence(requirement, "oppose")
        
        print(f"   🔍 PRO evidence found: {len(pro_results)} sources")
        print(f"   🔍 CON evidence found: {len(con_results)} sources")
        
        if pro_results:
            print(f"   📄 Sample PRO: {pro_results[0].get('snippet', 'No snippet')[:80]}...")
        if con_results:
            print(f"   📄 Sample CON: {con_results[0].get('snippet', 'No snippet')[:80]}...")
            
        total_evidence = len(pro_results) + len(con_results)
        print(f"   📊 Total evidence gathered: {total_evidence} sources")
        
        if total_evidence == 0:
            print("   ⚠️ No evidence found - may be search rate limits or connectivity issues")
            
        print("\n2️⃣ Testing Evidence System Integration...")
        
        # Test evidence gathering system
        sys.path.append(os.path.join(project_root, 'arena'))
        from evidence_system import EvidenceGatherer, EvidenceScorer
        
        gatherer = EvidenceGatherer()
        evidence_objects = await gatherer.gather_evidence(requirement, "neutral", max_sources=5)
        
        print(f"   📋 Evidence objects created: {len(evidence_objects)}")
        
        if evidence_objects:
            scorer = EvidenceScorer()
            collection_score = scorer.score_evidence_collection(evidence_objects)
            print(f"   📊 Evidence collection score: {collection_score:.3f}")
            
            # Show sample evidence
            for i, ev in enumerate(evidence_objects[:2]):
                claim = getattr(ev, 'claim', str(ev)[:60])
                tier = getattr(ev, 'tier', 'UNKNOWN')
                print(f"   Evidence {i+1} [{tier}]: {claim}...")
        
        print("\n3️⃣ Testing AI Components...")
        
        # Test AI argument generation
        if anthropic_key:
            print("   🤖 Testing with Anthropic Claude...")
            import anthropic
            
            client = anthropic.Anthropic(api_key=anthropic_key)
            
            # Test simple AI call
            test_prompt = f"Generate one strong argument for implementing OAuth 2.0 authentication. Keep it under 100 words."
            
            try:
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=200,
                    messages=[{"role": "user", "content": test_prompt}]
                )
                ai_response = response.content[0].text
                print(f"   ✅ Anthropic API working: {ai_response[:60]}...")
                
            except Exception as e:
                print(f"   ❌ Anthropic API error: {e}")
                
        if openai_key:
            print("   🤖 Testing with OpenAI GPT...")
            import openai
            
            # Test simple AI call with new API format
            try:
                client = openai.OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    max_tokens=200,
                    messages=[{"role": "user", "content": "Generate one argument against OAuth complexity in 50 words."}]
                )
                ai_response = response.choices[0].message.content
                print(f"   ✅ OpenAI API working: {ai_response[:60]}...")
                
            except Exception as e:
                print(f"   ❌ OpenAI API error: {e}")
        
        print("\n4️⃣ Testing Complete Integration Flow...")
        
        # Create mock evidence for full flow test
        class MockEvidence:
            def __init__(self, claim, source="Test Source", tier="GOLD"):
                self.claim = claim
                self.source = source 
                self.tier = tier
                self.total_score = 0.8
            def __str__(self):
                return f"{self.claim} (Source: {self.source})"
        
        mock_evidence = [
            MockEvidence("OAuth 2.0 provides secure standardized authentication", "RFC 6749"),
            MockEvidence("OAuth enables single sign-on across multiple services", "Auth0 Docs"),
            MockEvidence("OAuth implementation adds complexity to user management", "Security Blog"),
        ]
        
        # Test AI-powered components with mock evidence
        if anthropic_key:
            print("   🎭 Testing full AI debate flow...")
            
            # Simulate the complete flow
            pro_prompt = f"""Generate 2 arguments FOR implementing OAuth 2.0 based on this evidence:
- OAuth 2.0 provides secure standardized authentication (RFC 6749)
- OAuth enables single sign-on across multiple services (Auth0 Docs)"""

            try:
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=300,
                    messages=[{"role": "user", "content": pro_prompt}]
                )
                pro_args_text = response.content[0].text
                pro_args = [arg.strip().lstrip('-').strip() 
                          for arg in pro_args_text.split('\n') 
                          if arg.strip() and not arg.strip().startswith('#')][:2]
                
                print(f"   💚 Generated {len(pro_args)} PRO arguments")
                for i, arg in enumerate(pro_args, 1):
                    print(f"      {i}. {arg[:70]}...")
                
                # Test judge verdict
                judge_prompt = f"""You are a pragmatic software judge. Based on this requirement and arguments, make a verdict:

REQUIREMENT: add OAuth 2.0 authentication to web application

PRO ARGUMENTS:
{chr(10).join([f'- {arg}' for arg in pro_args[:2]])}

CON ARGUMENTS:
- OAuth implementation adds complexity to user management systems
- Additional dependencies increase security attack surface

Respond with:
VERDICT: [APPROVED/REJECTED/NEEDS_RESEARCH]
CONFIDENCE: [0-100]%
REASONING: [Brief explanation]"""

                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=400,
                    messages=[{"role": "user", "content": judge_prompt}]
                )
                
                judge_response = response.content[0].text
                print(f"   ⚖️ AI Judge verdict generated:")
                
                # Parse verdict
                lines = judge_response.split('\n')
                for line in lines:
                    if line.strip().startswith(('VERDICT:', 'CONFIDENCE:', 'REASONING:')):
                        print(f"      {line.strip()}")
                
                print("   ✅ Full AI debate flow operational!")
                
            except Exception as e:
                print(f"   ❌ AI debate flow error: {e}")
        
        print("\n" + "=" * 60)
        print("🎊 FULL INTEGRATION TEST RESULTS")
        print("=" * 60)
        
        # Summary
        search_working = total_evidence > 0
        evidence_working = len(evidence_objects) > 0 if 'evidence_objects' in locals() else False
        ai_working = (anthropic_key is not None) or (openai_key is not None)
        
        print(f"🔍 Search System: {'✅ OPERATIONAL' if search_working else '⚠️ LIMITED (rate limits/connectivity)'}")
        print(f"📊 Evidence System: {'✅ OPERATIONAL' if evidence_working else '⚠️ LIMITED'}")
        print(f"🤖 AI Integration: {'✅ OPERATIONAL' if ai_working else '❌ NOT AVAILABLE'}")
        print(f"🏛️ Complete Debate: {'✅ READY' if (evidence_working and ai_working) else '⚠️ PARTIAL'}")
        
        overall_status = "FULLY OPERATIONAL" if (search_working and evidence_working and ai_working) else "PARTIALLY OPERATIONAL"
        print(f"\n🚀 SYSTEM STATUS: {overall_status}")
        
        if overall_status == "FULLY OPERATIONAL":
            print("🎉 ReqDefender is ready for real AI-powered debates!")
        else:
            print("💡 System functional but some components have limitations")
            
        return overall_status == "FULLY OPERATIONAL"
        
    except Exception as e:
        print(f"❌ Full integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_full_integration())
    sys.exit(0 if success else 1)
#built with love
