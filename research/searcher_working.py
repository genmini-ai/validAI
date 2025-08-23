# research/searcher_working.py
"""Working research tools and search functionality for evidence gathering"""

from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from typing import List, Dict, Optional
import os
import json
from datetime import datetime
import asyncio
import aiohttp
import requests
import time
import threading
from collections import defaultdict


class WorkingResearchPipeline:
    """Production-ready research pipeline using DuckDuckGo by default, with optional Brave Search API"""
    
    def __init__(self):
        self.search_tools = self._initialize_search_tools()
        self.session = None
        
        # Rate limiting for Brave API (1 query/second)
        self._rate_limiter = defaultdict(list)
        self._rate_lock = threading.Lock()
        self._brave_available = True
        self._last_brave_call = 0
        self._min_delay_between_calls = 1.1  # 1.1 seconds to be safe
        self.api_call_count = 0
        
    def _initialize_search_tools(self) -> Dict:
        """Initialize available search tools - DuckDuckGo by default, Brave if API key provided"""
        tools = {}
        
        # DuckDuckGo (primary search engine, always available, no API key needed)
        tools["duckduckgo"] = DuckDuckGoSearchRun()
        
        # Direct Brave Search API (optional enhancement if API key available)
        if os.getenv("BRAVE_SEARCH_API_KEY") and "your_brave" not in os.getenv("BRAVE_SEARCH_API_KEY", ""):
            tools["brave_direct"] = self._create_brave_direct_search()
        
        return tools
    
    def _create_brave_direct_search(self):
        """Create direct Brave Search API caller"""
        def brave_search(query: str) -> List[Dict]:
            # Enforce rate limit: 1 query per second
            self._enforce_brave_rate_limit()
                
            try:
                url = "https://api.search.brave.com/res/v1/web/search"
                headers = {
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": os.getenv("BRAVE_SEARCH_API_KEY")
                }
                params = {
                    "q": query,
                    "count": 5,
                    "offset": 0,
                    "safesearch": "moderate",
                    "freshness": "py",  # Past year
                    "text_decorations": False,
                    "spellcheck": True
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                self.api_call_count += 1
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    for result in data.get("web", {}).get("results", [])[:5]:
                        results.append({
                            "title": result.get("title", ""),
                            "snippet": result.get("description", ""),
                            "url": result.get("url", ""),
                            "source": self._extract_domain(result.get("url", "")),
                            "published": result.get("age", "")
                        })
                    
                    print(f"✅ Brave Search: Found {len(results)} results for '{query[:30]}...'")
                    return results
                    
                elif response.status_code == 429:
                    print(f"⚠️  Brave API rate limit - switching to DuckDuckGo fallback")
                    self._brave_available = False
                    return self._use_duckduckgo_fallback(query)
                    
                else:
                    print(f"⚠️  Brave Search API error {response.status_code} - using DuckDuckGo fallback")
                    return self._use_duckduckgo_fallback(query)
                    
            except Exception as e:
                print(f"❌ Brave Search failed: {e} - using DuckDuckGo fallback")
                return self._use_duckduckgo_fallback(query)
        
        return brave_search
    
    def _enforce_brave_rate_limit(self):
        """Enforce Brave API rate limit: 1 query per second"""
        current_time = time.time()
        
        with self._rate_lock:
            # Calculate time since last call
            time_since_last_call = current_time - self._last_brave_call
            
            # If we need to wait, sleep for the remaining time
            if time_since_last_call < self._min_delay_between_calls:
                wait_time = self._min_delay_between_calls - time_since_last_call
                print(f"⏱️  Rate limiting: waiting {wait_time:.1f}s for Brave API")
                time.sleep(wait_time)
            
            # Update last call time
            self._last_brave_call = time.time()
    
    def _use_duckduckgo_fallback(self, query: str) -> List[Dict]:
        """Use DuckDuckGo as fallback when Brave API fails"""
        try:
            ddg_search = DuckDuckGoSearchRun()
            raw_results = ddg_search.run(query)
            
            # Parse DuckDuckGo results into our standard format
            results = []
            if raw_results:
                # DuckDuckGo returns text, try to extract useful info
                lines = raw_results.split('\n')[:3]  # Take first 3 results
                for i, line in enumerate(lines):
                    if line.strip():
                        results.append({
                            "title": f"DuckDuckGo Result {i+1}",
                            "snippet": line.strip()[:200],
                            "url": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
                            "source": "DuckDuckGo",
                            "published": "Recent"
                        })
            
            print(f"🦆 DuckDuckGo fallback: Found {len(results)} results for '{query[:30]}...'")
            return results
            
        except Exception as e:
            print(f"❌ DuckDuckGo fallback failed: {e}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return "unknown"
    
    async def search_evidence(self, requirement: str, stance: str = "neutral") -> List[Dict]:
        """Search for evidence about a requirement"""
        print(f"🔍 Searching for evidence: {requirement} (stance: {stance})")
        
        # Generate targeted search queries
        queries = self._generate_search_queries(requirement, stance)
        
        all_results = []
        # Limit queries to respect rate limits (1 query/second = slow!)
        max_queries = int(os.getenv("MAX_EVIDENCE_QUERIES", "2"))  # Configurable
        for query in queries[:max_queries]:
            # Use Brave Search if API key is available (enhanced results)
            if "brave_direct" in self.search_tools:
                print(f"  Using Brave Search for: {query}")
                results = self.search_tools["brave_direct"](query)
                all_results.extend(results)
            
            # Use DuckDuckGo (default, no API key required)
            elif "duckduckgo" in self.search_tools:
                print(f"  Using DuckDuckGo for: {query}")
                try:
                    duckduckgo_result = self.search_tools["duckduckgo"].run(query)
                    # Parse DuckDuckGo result (it returns text, not structured data)
                    parsed_results = self._parse_duckduckgo_result(duckduckgo_result, query)
                    all_results.extend(parsed_results)
                except Exception as e:
                    print(f"  DuckDuckGo search failed: {e}")
        
        print(f"✅ Found {len(all_results)} total evidence pieces")
        return all_results[:10]  # Limit results
    
    def _generate_search_queries(self, requirement: str, stance: str) -> List[str]:
        """Generate targeted search queries"""
        base_queries = []
        
        if stance == "support":
            base_queries = [
                f"{requirement} success case study",
                f"{requirement} benefits ROI results",
                f"{requirement} implementation guide best practices"
            ]
        elif stance == "oppose":
            base_queries = [
                f"{requirement} failed problems issues",
                f"{requirement} why not disadvantages",
                f"{requirement} alternatives better solution"
            ]
        else:  # neutral
            base_queries = [
                f"{requirement} analysis pros and cons",
                f"{requirement} implementation cost time",
                f"{requirement} market research adoption"
            ]
        
        return base_queries
    
    def _parse_duckduckgo_result(self, result_text: str, query: str) -> List[Dict]:
        """Parse DuckDuckGo text result into structured format"""
        # DuckDuckGo returns plain text, so we create a single evidence item
        return [{
            "title": f"Research: {query}",
            "snippet": result_text[:300] + "..." if len(result_text) > 300 else result_text,
            "url": "https://duckduckgo.com",
            "source": "duckduckgo.com",
            "published": "recent"
        }]
    
    def search_specific_sites(self, requirement: str, sites: List[str]) -> List[Dict]:
        """Search specific sites for evidence"""
        all_results = []
        
        for site in sites:
            query = f"site:{site} {requirement}"
            
            if "brave_direct" in self.search_tools:
                results = self.search_tools["brave_direct"](query)
                all_results.extend(results)
        
        return all_results
    
    def get_usage_stats(self) -> Dict:
        """Get API usage statistics"""
        return {
            "brave_api_calls": self.api_call_count,
            "available_tools": list(self.search_tools.keys()),
            "cost_estimate": self.api_call_count * 0.001  # Rough estimate
        }


def create_working_research_tools() -> List[Tool]:
    """Create working LangChain tools for agent use"""
    pipeline = WorkingResearchPipeline()
    
    tools = []
    
    # Evidence search tool
    tools.append(Tool(
        name="Search Evidence",
        func=lambda q: asyncio.run(pipeline.search_evidence(q, "neutral")),
        description="Search for evidence about a requirement"
    ))
    
    # Academic/Industry sites search
    tools.append(Tool(
        name="Search Academic Sources", 
        func=lambda q: pipeline.search_specific_sites(q, [
            "scholar.google.com", "arxiv.org", "gartner.com", "forrester.com"
        ]),
        description="Search academic and industry sources"
    ))
    
    # Technical sites search  
    tools.append(Tool(
        name="Search Technical Sources",
        func=lambda q: pipeline.search_specific_sites(q, [
            "github.com", "stackoverflow.com", "dev.to", "hackernews.com"
        ]),
        description="Search technical documentation and communities"
    ))
    
    return tools


def test_research_pipeline():
    """Test the research pipeline"""
    print("🧪 Testing Working Research Pipeline")
    print("=" * 40)
    
    pipeline = WorkingResearchPipeline()
    
    print(f"Available tools: {list(pipeline.search_tools.keys())}")
    
    # Test search
    try:
        results = asyncio.run(pipeline.search_evidence("blockchain todo app", "oppose"))
        print(f"✅ Search completed: {len(results)} results")
        
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. {result.get('title', 'No title')[:50]}...")
            print(f"     Source: {result.get('source', 'Unknown')}")
        
        # Show usage
        stats = pipeline.get_usage_stats()
        print(f"\n📊 Usage Stats:")
        print(f"  API calls: {stats['brave_api_calls']}")
        print(f"  Estimated cost: ${stats['cost_estimate']:.3f}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_research_pipeline()
#built with love
