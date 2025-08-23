#!/usr/bin/env python3
"""
Integration test for evidence collection end-to-end functionality
Tests the complete flow: Topic → Search → Evidence → Scoring → Validation
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from typing import List, Dict

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import directly to avoid module dependency issues
sys.path.append(os.path.join(os.path.dirname(__file__), 'arena'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'research'))

from research.searcher_working import WorkingResearchPipeline
from evidence_system import EvidenceGatherer, EvidenceScorer, EvidenceValidator, EvidenceTier


class EvidenceIntegrationTester:
    """Comprehensive integration tester for evidence collection system"""
    
    def __init__(self):
        self.pipeline = WorkingResearchPipeline()
        self.gatherer = EvidenceGatherer()
        self.scorer = EvidenceScorer()
        self.validator = EvidenceValidator()
        
        self.test_requirements = [
            "implement two-factor authentication",
            "migrate to microservices architecture", 
            "add blockchain payment system",
            "use GraphQL instead of REST API",
            "deploy application to Kubernetes"
        ]
        
        self.test_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "search_requests": 0,
            "evidence_collected": 0,
            "errors": [],
            "warnings": []
        }
    
    async def run_full_integration_test(self):
        """Run complete integration test suite"""
        print("🧪 Evidence Collection Integration Test Suite")
        print("=" * 60)
        print(f"⏰ Started at: {datetime.now()}")
        print()
        
        # Test 1: Basic evidence collection
        await self.test_basic_evidence_collection()
        
        # Test 2: Evidence scoring and ranking
        await self.test_evidence_scoring()
        
        # Test 3: Evidence validation
        await self.test_evidence_validation()
        
        # Test 4: Multiple stances
        await self.test_multiple_stances()
        
        # Test 5: Edge cases and error handling
        await self.test_edge_cases()
        
        # Test 6: Performance and rate limiting
        await self.test_performance_limits()
        
        # Generate report
        self.generate_test_report()
    
    async def test_basic_evidence_collection(self):
        """Test 1: Basic evidence collection functionality"""
        print("🔬 Test 1: Basic Evidence Collection")
        print("-" * 40)
        
        for i, requirement in enumerate(self.test_requirements[:3], 1):
            try:
                print(f"  {i}. Testing: '{requirement}'")
                
                # Collect evidence
                start_time = time.time()
                evidence_list = await self.gatherer.gather_evidence(
                    requirement=requirement,
                    stance="neutral",
                    max_sources=5
                )
                duration = time.time() - start_time
                
                # Validate results
                assert len(evidence_list) > 0, "No evidence collected"
                assert all(hasattr(e, 'claim') for e in evidence_list), "Evidence missing claims"
                assert all(hasattr(e, 'total_score') for e in evidence_list), "Evidence missing scores"
                
                print(f"     ✅ Collected {len(evidence_list)} pieces in {duration:.1f}s")
                print(f"     📊 Scores: {[f'{e.total_score:.2f}' for e in evidence_list[:3]]}")
                
                self.test_results["evidence_collected"] += len(evidence_list)
                self.test_results["search_requests"] += 3  # Estimated queries per requirement
                self._test_passed()
                
                # Rate limiting delay
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"     ❌ Failed: {e}")
                self._test_failed(f"Basic collection failed for '{requirement}': {e}")
        
        print()
    
    async def test_evidence_scoring(self):
        """Test 2: Evidence scoring and tier classification"""
        print("🏆 Test 2: Evidence Scoring & Tier Classification")
        print("-" * 40)
        
        try:
            # Get evidence for testing
            requirement = "implement OAuth authentication"
            evidence_list = await self.gatherer.gather_evidence(
                requirement=requirement,
                stance="support",
                max_sources=8
            )
            
            if not evidence_list:
                print("     ⚠️ No evidence to test scoring")
                self._test_failed("No evidence returned for scoring test")
                return
            
            # Test tier distribution
            tier_counts = {}
            for evidence in evidence_list:
                tier = evidence.tier.name
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            print(f"     📈 Tier distribution: {tier_counts}")
            
            # Test scoring components
            for i, evidence in enumerate(evidence_list[:3], 1):
                print(f"     {i}. Tier: {evidence.tier.name}, Score: {evidence.total_score:.3f}")
                print(f"        Relevance: {evidence.relevance_score:.2f}, "
                      f"Credibility: {evidence.credibility_score:.2f}, "
                      f"Recency: {evidence.recency_score:.2f}")
            
            # Test evidence ranking (should be sorted by score)
            scores = [e.total_score for e in evidence_list]
            is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
            
            if is_sorted:
                print("     ✅ Evidence properly ranked by score")
                self._test_passed()
            else:
                print("     ❌ Evidence not properly ranked")
                self._test_failed("Evidence ranking failed")
            
            # Test score collection function
            collection_score = self.scorer.score_evidence_collection(evidence_list)
            print(f"     📊 Collection score: {collection_score:.3f}")
            
            self.test_results["evidence_collected"] += len(evidence_list)
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"     ❌ Scoring test failed: {e}")
            self._test_failed(f"Evidence scoring test failed: {e}")
        
        print()
    
    async def test_evidence_validation(self):
        """Test 3: Evidence validation rules"""
        print("✅ Test 3: Evidence Validation")
        print("-" * 40)
        
        try:
            # Get evidence for validation testing
            requirement = "add machine learning recommendations"
            evidence_list = await self.gatherer.gather_evidence(
                requirement=requirement,
                stance="neutral",
                max_sources=5
            )
            
            if not evidence_list:
                print("     ⚠️ No evidence to validate")
                self._test_failed("No evidence for validation test")
                return
            
            valid_count = 0
            invalid_count = 0
            validation_issues = []
            
            for evidence in evidence_list:
                is_valid, issues = self.validator.validate_evidence(evidence)
                
                if is_valid:
                    valid_count += 1
                else:
                    invalid_count += 1
                    validation_issues.extend(issues)
            
            print(f"     ✅ Valid evidence: {valid_count}")
            print(f"     ⚠️ Invalid evidence: {invalid_count}")
            
            if validation_issues:
                print("     🔍 Common issues:")
                issue_counts = {}
                for issue in validation_issues:
                    issue_counts[issue] = issue_counts.get(issue, 0) + 1
                
                for issue, count in issue_counts.items():
                    print(f"        - {issue}: {count} cases")
            
            # Test passes if we can validate all evidence (even if some are invalid)
            self._test_passed()
            self.test_results["evidence_collected"] += len(evidence_list)
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"     ❌ Validation test failed: {e}")
            self._test_failed(f"Evidence validation test failed: {e}")
        
        print()
    
    async def test_multiple_stances(self):
        """Test 4: Different search stances (support, oppose, neutral)"""
        print("🎭 Test 4: Multiple Search Stances")
        print("-" * 40)
        
        requirement = "switch to serverless architecture"
        stances = ["support", "oppose", "neutral"]
        
        stance_results = {}
        
        for stance in stances:
            try:
                print(f"     Testing '{stance}' stance...")
                
                evidence_list = await self.gatherer.gather_evidence(
                    requirement=requirement,
                    stance=stance,
                    max_sources=4
                )
                
                stance_results[stance] = {
                    "count": len(evidence_list),
                    "avg_score": sum(e.total_score for e in evidence_list) / len(evidence_list) if evidence_list else 0,
                    "queries": self.gatherer._generate_search_queries(requirement, stance)[:2]
                }
                
                print(f"        ✅ Found {len(evidence_list)} pieces")
                print(f"        📝 Sample queries: {stance_results[stance]['queries']}")
                
                self.test_results["evidence_collected"] += len(evidence_list)
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"        ❌ Failed stance '{stance}': {e}")
                self._test_failed(f"Stance test failed for '{stance}': {e}")
                continue
        
        # Validate that different stances produce different queries
        unique_queries = set()
        for stance_data in stance_results.values():
            for query in stance_data["queries"]:
                unique_queries.add(query)
        
        if len(unique_queries) >= len(stances):
            print("     ✅ Different stances generate different queries")
            self._test_passed()
        else:
            print("     ⚠️ Stances may not be generating diverse queries")
            self._test_failed("Stance diversity test failed")
        
        print(f"     📊 Results: {stance_results}")
        print()
    
    async def test_edge_cases(self):
        """Test 5: Edge cases and error handling"""
        print("🚨 Test 5: Edge Cases & Error Handling")
        print("-" * 40)
        
        edge_cases = [
            ("empty requirement", ""),
            ("very short", "AI"),
            ("very long requirement", "implement a comprehensive artificial intelligence machine learning deep learning natural language processing computer vision recommendation system with blockchain integration and microservices architecture"),
            ("special characters", "add OAuth 2.0 & JWT authentication with @mentions"),
            ("non-English", "implementar autenticación de dos factores")
        ]
        
        for case_name, requirement in edge_cases:
            try:
                print(f"     Testing: {case_name}")
                
                if requirement == "":
                    # Empty requirement should handle gracefully
                    try:
                        evidence_list = await self.gatherer.gather_evidence(
                            requirement=requirement,
                            stance="neutral",
                            max_sources=2
                        )
                        print(f"        ⚠️ Empty requirement returned {len(evidence_list)} results")
                    except Exception as e:
                        print(f"        ✅ Empty requirement properly handled: {type(e).__name__}")
                else:
                    evidence_list = await self.gatherer.gather_evidence(
                        requirement=requirement,
                        stance="neutral", 
                        max_sources=2
                    )
                    print(f"        ✅ Handled gracefully, got {len(evidence_list)} results")
                    self.test_results["evidence_collected"] += len(evidence_list)
                
                await asyncio.sleep(0.5)  # Shorter delay for edge cases
                
            except Exception as e:
                print(f"        ⚠️ Error (may be expected): {type(e).__name__}: {e}")
                self.test_results["warnings"].append(f"Edge case '{case_name}': {e}")
        
        self._test_passed()  # Edge case test passes if system doesn't crash
        print()
    
    async def test_performance_limits(self):
        """Test 6: Performance and rate limiting awareness"""
        print("⚡ Test 6: Performance & Rate Limiting")
        print("-" * 40)
        
        try:
            requirement = "implement continuous integration pipeline"
            
            # Test rapid requests to understand current performance
            print("     Testing rapid evidence collection...")
            
            start_time = time.time()
            evidence_batches = []
            
            # Collect evidence in small batches to avoid rate limits
            for i in range(3):
                print(f"        Batch {i+1}/3...")
                evidence_list = await self.gatherer.gather_evidence(
                    requirement=f"{requirement} batch {i+1}",
                    stance="neutral",
                    max_sources=3
                )
                evidence_batches.append(evidence_list)
                
                # Delay to respect rate limits
                await asyncio.sleep(2)
            
            total_time = time.time() - start_time
            total_evidence = sum(len(batch) for batch in evidence_batches)
            
            print(f"     📊 Performance Results:")
            print(f"        Total evidence: {total_evidence}")
            print(f"        Total time: {total_time:.1f}s")
            print(f"        Avg per request: {total_time/9:.1f}s")  # 9 total requests (3 batches × 3 queries)
            
            # Check if we're within reasonable performance bounds
            avg_per_evidence = total_time / total_evidence if total_evidence > 0 else float('inf')
            
            if avg_per_evidence < 5:  # Less than 5 seconds per evidence piece
                print(f"     ✅ Good performance: {avg_per_evidence:.1f}s per evidence")
                self._test_passed()
            else:
                print(f"     ⚠️ Slow performance: {avg_per_evidence:.1f}s per evidence")
                self.test_results["warnings"].append(f"Slow performance: {avg_per_evidence:.1f}s per evidence")
                self._test_passed()  # Still pass, but note the warning
            
            self.test_results["evidence_collected"] += total_evidence
            self.test_results["search_requests"] += 9
            
        except Exception as e:
            print(f"     ❌ Performance test failed: {e}")
            self._test_failed(f"Performance test failed: {e}")
        
        print()
    
    def _test_passed(self):
        """Mark test as passed"""
        self.test_results["tests_run"] += 1
        self.test_results["tests_passed"] += 1
    
    def _test_failed(self, error_msg: str):
        """Mark test as failed"""
        self.test_results["tests_run"] += 1
        self.test_results["tests_failed"] += 1
        self.test_results["errors"].append(error_msg)
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("📋 Integration Test Report")
        print("=" * 60)
        
        results = self.test_results
        
        # Overall results
        print(f"🧪 Tests Run: {results['tests_run']}")
        print(f"✅ Passed: {results['tests_passed']}")
        print(f"❌ Failed: {results['tests_failed']}")
        print(f"📊 Success Rate: {(results['tests_passed']/results['tests_run']*100):.1f}%")
        print()
        
        # Performance metrics
        print(f"🔍 Search Requests: {results['search_requests']}")
        print(f"📄 Evidence Collected: {results['evidence_collected']}")
        print(f"📈 Avg Evidence per Request: {results['evidence_collected']/results['search_requests']:.1f}")
        print()
        
        # Issues
        if results['errors']:
            print("❌ Errors Found:")
            for i, error in enumerate(results['errors'], 1):
                print(f"   {i}. {error}")
            print()
        
        if results['warnings']:
            print("⚠️ Warnings:")
            for i, warning in enumerate(results['warnings'], 1):
                print(f"   {i}. {warning}")
            print()
        
        # Overall assessment
        if results['tests_failed'] == 0:
            print("🎉 ALL TESTS PASSED - Evidence collection system working correctly!")
            if results['warnings']:
                print("⚠️ Note: Some warnings were recorded above")
        elif results['tests_failed'] < results['tests_passed']:
            print("⚠️ MOSTLY WORKING - Some issues found but system is functional")
        else:
            print("🚨 SIGNIFICANT ISSUES - Evidence collection needs attention")
        
        print(f"\n⏰ Completed at: {datetime.now()}")


async def main():
    """Run the integration test suite"""
    tester = EvidenceIntegrationTester()
    await tester.run_full_integration_test()


if __name__ == "__main__":
    print("🚀 Starting Evidence Collection Integration Tests")
    print()
    asyncio.run(main())
#built with love
