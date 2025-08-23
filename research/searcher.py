# research/searcher.py
"""Research tools and search functionality for evidence gathering"""

from langchain_community.tools import BraveSearchResults, DuckDuckGoSearchRun
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain.tools import Tool
from typing import List, Dict, Optional
import os
import json
from datetime import datetime
import asyncio
import aiohttp


class ResearchPipeline:
    """Manages multi-source research for evidence gathering"""
    
    def __init__(self):
        self.search_tools = self._initialize_search_tools()
        self.session = None
        
    def _initialize_search_tools(self) -> Dict:
        """Initialize available search tools based on API keys"""
        tools = {}
        
        # Brave Search (preferred for quality results)
        if os.getenv("BRAVE_SEARCH_API_KEY"):
            tools["brave"] = BraveSearchResults(
                max_results=5,
                search_depth="advanced"
            )
        
        # DuckDuckGo (no API key required, fallback)
        tools["duckduckgo"] = DuckDuckGoSearchRun()
        
        # Google Search (if configured)
        if os.getenv("GOOGLE_API_KEY") and os.getenv("GOOGLE_CSE_ID"):
            google_wrapper = GoogleSearchAPIWrapper()
            tools["google"] = Tool(
                name="Google Search",
                func=google_wrapper.run,
                description="Search Google for information"
            )
        
        return tools
    
    async def search_academic(self, query: str) -> List[Dict]:
        """Search academic sources for peer-reviewed evidence"""
        results = []
        
        # Search arXiv
        arxiv_results = await self._search_arxiv(query)
        results.extend(arxiv_results)
        
        # Search Google Scholar (via Brave/Google with site filter)
        scholar_query = f"site:scholar.google.com OR site:arxiv.org OR site:acm.org {query}"
        if "brave" in self.search_tools:
            scholar_results = await self._run_search(self.search_tools["brave"], scholar_query)
            results.extend(scholar_results)
        
        return results
    
    async def search_industry(self, query: str) -> List[Dict]:
        """Search industry reports and analysis"""
        industry_sites = [
            "gartner.com",
            "forrester.com", 
            "mckinsey.com",
            "deloitte.com",
            "accenture.com"
        ]
        
        results = []
        for site in industry_sites:
            site_query = f"site:{site} {query}"
            if "brave" in self.search_tools:
                site_results = await self._run_search(self.search_tools["brave"], site_query)
                results.extend(site_results)
        
        return results
    
    async def search_technical(self, query: str) -> List[Dict]:
        """Search technical communities and documentation"""
        tech_query = f"site:github.com OR site:stackoverflow.com OR site:dev.to {query}"
        
        results = []
        if "brave" in self.search_tools:
            results = await self._run_search(self.search_tools["brave"], tech_query)
        else:
            # Fallback to DuckDuckGo
            results = await self._run_search(self.search_tools["duckduckgo"], query)
        
        return results
    
    async def search_failures(self, requirement: str) -> List[Dict]:
        """Specifically search for failure cases and post-mortems"""
        failure_queries = [
            f"{requirement} failed project",
            f"{requirement} post-mortem",
            f"{requirement} lessons learned",
            f"why {requirement} doesn't work",
            f"{requirement} problems issues challenges"
        ]
        
        all_results = []
        for query in failure_queries:
            if "brave" in self.search_tools:
                results = await self._run_search(self.search_tools["brave"], query)
                all_results.extend(results)
        
        return all_results
    
    async def search_alternatives(self, requirement: str) -> List[Dict]:
        """Search for alternatives to the requirement"""
        alternative_queries = [
            f"alternatives to {requirement}",
            f"instead of {requirement}",
            f"{requirement} vs",
            f"better than {requirement}"
        ]
        
        all_results = []
        for query in alternative_queries:
            tool = self.search_tools.get("brave", self.search_tools["duckduckgo"])
            results = await self._run_search(tool, query)
            all_results.extend(results)
        
        return all_results
    
    async def _search_arxiv(self, query: str) -> List[Dict]:
        """Search arXiv for academic papers"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": query,
            "max_results": 5,
            "sortBy": "relevance"
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    # Parse XML response (simplified)
                    content = await response.text()
                    results = self._parse_arxiv_response(content)
                    return results
        except Exception as e:
            print(f"arXiv search error: {e}")
        
        return []
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict]:
        """Parse arXiv XML response"""
        # Simplified parsing - in production use proper XML parser
        results = []
        
        # Basic extraction (would use xml.etree or BeautifulSoup in production)
        entries = xml_content.split("<entry>")[1:]  # Skip header
        
        for entry in entries[:5]:  # Limit to 5 results
            try:
                title_start = entry.find("<title>") + 7
                title_end = entry.find("</title>")
                title = entry[title_start:title_end].strip()
                
                summary_start = entry.find("<summary>") + 9
                summary_end = entry.find("</summary>")
                summary = entry[summary_start:summary_end].strip()
                
                link_start = entry.find('<link href="') + 12
                link_end = entry.find('"', link_start)
                link = entry[link_start:link_end]
                
                results.append({
                    "title": title,
                    "snippet": summary[:200],
                    "url": link,
                    "source": "arxiv.org"
                })
            except:
                continue
        
        return results
    
    async def _run_search(self, tool, query: str) -> List[Dict]:
        """Run a search with error handling"""
        try:
            result = await asyncio.to_thread(tool.run, query)
            
            # Parse result based on tool type
            if isinstance(result, str):
                try:
                    # Try to parse as JSON
                    parsed = json.loads(result)
                    if isinstance(parsed, list):
                        return parsed
                    elif isinstance(parsed, dict) and "results" in parsed:
                        return parsed["results"]
                except:
                    # Return as single result if not JSON
                    return [{
                        "title": query,
                        "snippet": result[:500],
                        "url": "",
                        "source": "search"
                    }]
            elif isinstance(result, list):
                return result
            else:
                return []
        except Exception as e:
            print(f"Search error for query '{query}': {e}")
            return []
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()


def create_research_tools() -> List[Tool]:
    """Create LangChain tools for agent use"""
    pipeline = ResearchPipeline()
    
    tools = []
    
    # Academic search tool
    tools.append(Tool(
        name="Search Academic Papers",
        func=lambda q: asyncio.run(pipeline.search_academic(q)),
        description="Search academic papers and peer-reviewed research"
    ))
    
    # Industry research tool
    tools.append(Tool(
        name="Search Industry Reports",
        func=lambda q: asyncio.run(pipeline.search_industry(q)),
        description="Search industry analyst reports and market research"
    ))
    
    # Technical documentation tool
    tools.append(Tool(
        name="Search Technical Docs",
        func=lambda q: asyncio.run(pipeline.search_technical(q)),
        description="Search GitHub, StackOverflow, and technical documentation"
    ))
    
    # Failure cases tool
    tools.append(Tool(
        name="Search Failure Cases",
        func=lambda q: asyncio.run(pipeline.search_failures(q)),
        description="Search for post-mortems and failure cases"
    ))
    
    # Alternatives tool
    tools.append(Tool(
        name="Search Alternatives",
        func=lambda q: asyncio.run(pipeline.search_alternatives(q)),
        description="Search for alternative approaches and solutions"
    ))
    
    return tools


class ResearchCache:
    """Cache research results to avoid duplicate searches"""
    
    def __init__(self, ttl_hours: int = 24):
        self.cache = {}
        self.ttl_hours = ttl_hours
    
    def get(self, query: str) -> Optional[List[Dict]]:
        """Get cached results if still valid"""
        if query in self.cache:
            cached_time, results = self.cache[query]
            age_hours = (datetime.now() - cached_time).total_seconds() / 3600
            
            if age_hours < self.ttl_hours:
                return results
            else:
                del self.cache[query]
        
        return None
    
    def set(self, query: str, results: List[Dict]):
        """Cache search results"""
        self.cache[query] = (datetime.now(), results)
    
    def clear(self):
        """Clear the cache"""
        self.cache = {}
#built with love
