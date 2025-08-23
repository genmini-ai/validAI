#!/usr/bin/env python3
"""
Test script for Multi-Round Debate API
Tests the real debate interaction between agents
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_HOST = os.getenv("TEST_HOST", "localhost")
API_PORT = os.getenv("DEBATE_API_PORT", "8004")
API_URL = f"http://{API_HOST}:{API_PORT}"

async def test_health():
    """Test API health"""
    print("\n🏥 Testing API Health...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_URL}/health") as response:
                data = await response.json()
                print(f"✅ API Status: {data['status']}")
                print(f"   AI Available: {data['ai_available']}")
                return data['ai_available']
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

async def test_quick_debate():
    """Test quick 2-round debate"""
    print("\n⚡ Testing Quick Debate (2 rounds)...")
    
    requirement = "Add AI-powered code review suggestions in the IDE"
    
    async with aiohttp.ClientSession() as session:
        try:
            print(f"📝 Requirement: {requirement}")
            print("🎭 Starting debate...")
            
            start_time = datetime.now()
            
            async with session.post(
                f"{API_URL}/quick-debate",
                params={"requirement": requirement}
            ) as response:
                data = await response.json()
                
                duration = (datetime.now() - start_time).total_seconds()
                
                print(f"\n⚖️  VERDICT: {data['verdict']}")
                print(f"📊 Confidence: {data['confidence']:.1f}%")
                print(f"⏱️  Duration: {duration:.1f}s (reported: {data['duration']})")
                print(f"🔄 Rounds: {data['rounds_completed']}")
                
                print(f"\n💚 PRO Closing:")
                print(f"   {data['pro_closing']}")
                
                print(f"\n❌ CON Closing:")
                print(f"   {data['con_closing']}")
                
                print(f"\n🧑‍⚖️ Judge Summary:")
                print(f"   {data['summary']}")
                
                return True
                
        except Exception as e:
            print(f"❌ Quick debate failed: {e}")
            return False

async def test_full_debate():
    """Test full multi-round debate"""
    print("\n🎯 Testing Full Debate (3 rounds)...")
    
    requirement = "Implement blockchain-based user authentication system"
    
    async with aiohttp.ClientSession() as session:
        try:
            print(f"📝 Requirement: {requirement}")
            print("🎭 Starting multi-round debate...")
            
            request_data = {
                "requirement": requirement,
                "num_rounds": 3
            }
            
            start_time = datetime.now()
            
            async with session.post(
                f"{API_URL}/debate",
                json=request_data
            ) as response:
                data = await response.json()
                
                if data['success']:
                    transcript = data['transcript']
                    
                    print(f"\n⚖️  VERDICT: {data['verdict']}")
                    print(f"📊 Confidence: {data['confidence']:.1f}%")
                    print(f"⏱️  Duration: {data['duration_seconds']:.1f}s")
                    print(f"🔄 Total Rounds: {data['total_rounds']}")
                    
                    # Show round-by-round progression
                    print("\n📜 DEBATE TRANSCRIPT:")
                    print("=" * 60)
                    
                    for round_data in transcript['rounds']:
                        round_num = round_data['round_number']
                        round_type = round_data['round_type']
                        
                        print(f"\n🎯 ROUND {round_num} - {round_type.upper()}")
                        print("-" * 40)
                        
                        # PRO arguments
                        print("💚 PRO Team:")
                        for i, arg in enumerate(round_data['pro_arguments'][:2], 1):
                            print(f"   {i}. {arg[:150]}...")
                        
                        if round_data['pro_references_con']:
                            print(f"   → Responding to: {', '.join(round_data['pro_references_con'][:2])}")
                        
                        # CON arguments
                        print("\n❌ CON Team:")
                        for i, arg in enumerate(round_data['con_arguments'][:2], 1):
                            print(f"   {i}. {arg[:150]}...")
                        
                        if round_data['con_references_pro']:
                            print(f"   → Responding to: {', '.join(round_data['con_references_pro'][:2])}")
                    
                    # Final summaries
                    print("\n🎤 CLOSING STATEMENTS:")
                    print("-" * 40)
                    print("💚 PRO Summary:")
                    print(f"   {transcript['final_summaries']['PRO'][:300]}...")
                    print("\n❌ CON Summary:")
                    print(f"   {transcript['final_summaries']['CON'][:300]}...")
                    
                    # Judge verdict details
                    verdict = transcript['judge_verdict']
                    print("\n🧑‍⚖️ JUDGE'S DECISION:")
                    print("-" * 40)
                    print(f"Verdict: {verdict['verdict']} ({verdict['confidence']:.1f}% confidence)")
                    print(f"Reasoning: {verdict['reasoning']}")
                    
                    if verdict.get('winning_arguments'):
                        print("\n✅ Winning Arguments:")
                        for arg in verdict['winning_arguments']:
                            print(f"   • {arg}")
                    
                    if verdict.get('losing_weaknesses'):
                        print("\n⚠️  Losing Weaknesses:")
                        for weak in verdict['losing_weaknesses']:
                            print(f"   • {weak}")
                    
                    if verdict.get('decisive_factors'):
                        print(f"\n🎯 Decisive Factors: {verdict['decisive_factors']}")
                    
                    return True
                else:
                    print(f"❌ Debate failed: {data}")
                    return False
                    
        except Exception as e:
            print(f"❌ Full debate failed: {e}")
            return False

async def test_debate_comparison():
    """Compare same requirement with different round counts"""
    print("\n🔬 Testing Debate Depth Comparison...")
    
    requirement = "Add real-time collaborative editing features"
    
    async with aiohttp.ClientSession() as session:
        results = {}
        
        for num_rounds in [2, 3, 4]:
            print(f"\n📊 Testing with {num_rounds} rounds...")
            
            request_data = {
                "requirement": requirement,
                "num_rounds": num_rounds
            }
            
            try:
                async with session.post(
                    f"{API_URL}/debate",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    data = await response.json()
                    
                    results[num_rounds] = {
                        "verdict": data['verdict'],
                        "confidence": data['confidence'],
                        "duration": data['duration_seconds']
                    }
                    
                    print(f"   Verdict: {data['verdict']} ({data['confidence']:.1f}%)")
                    print(f"   Duration: {data['duration_seconds']:.1f}s")
                    
            except Exception as e:
                print(f"   Failed: {e}")
                results[num_rounds] = {"error": str(e)}
        
        # Compare results
        print("\n📈 COMPARISON RESULTS:")
        print("-" * 40)
        for rounds, result in results.items():
            if "error" not in result:
                print(f"{rounds} rounds: {result['verdict']} "
                      f"({result['confidence']:.1f}% in {result['duration']:.1f}s)")
            else:
                print(f"{rounds} rounds: ERROR - {result['error'][:50]}")
        
        return len([r for r in results.values() if "error" not in r]) > 0

async def main():
    """Run all tests"""
    print("=" * 60)
    print("🎭 MULTI-ROUND DEBATE API TEST SUITE")
    print("=" * 60)
    
    # Check if API is ready
    ai_available = await test_health()
    
    if not ai_available:
        print("\n⚠️  Warning: AI not available, using fallback templates")
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if await test_quick_debate():
        tests_passed += 1
    
    if await test_full_debate():
        tests_passed += 1
    
    if await test_debate_comparison():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 TEST SUMMARY: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! Multi-round debates working correctly.")
    else:
        print(f"⚠️  Some tests failed. Check configuration and retry.")
    
    print("=" * 60)

if __name__ == "__main__":
    print(f"🔧 Testing against: {API_URL}")
    print(f"   Make sure api_debate.py is running on port {API_PORT}")
    asyncio.run(main())
#built with love
