# arena/evidence.py
"""Evidence gathering, validation, and scoring system"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import asyncio
import hashlib
import json
from datetime import datetime, timedelta
from research.searcher_working import WorkingResearchPipeline
import re


class EvidenceTier(Enum):
    """Evidence quality tiers"""
    PLATINUM = 1  # Peer-reviewed, post-mortems, direct data
    GOLD = 2      # Industry reports, expert opinions
    SILVER = 3    # Blog posts, conference talks
    BRONZE = 4    # Opinions, analogies


@dataclass
class Evidence:
    """Structured evidence object"""
    claim: str
    source: str
    url: str
    tier: EvidenceTier
    relevance_score: float  # 0-1
    recency_score: float    # 0-1
    credibility_score: float  # 0-1
    raw_text: str
    extracted_data: Optional[Dict] = None
    counter_evidence: Optional[List] = None
    supporting_evidence: Optional[List] = None
    
    @property
    def total_score(self) -> float:
        """Calculate total evidence score"""
        tier_weights = {
            EvidenceTier.PLATINUM: 10,
            EvidenceTier.GOLD: 5,
            EvidenceTier.SILVER: 2,
            EvidenceTier.BRONZE: 1
        }
        
        base_weight = tier_weights[self.tier]
        return base_weight * self.relevance_score * self.recency_score * self.credibility_score
    
    @property
    def hash(self) -> str:
        """Generate unique hash for evidence"""
        content = f"{self.source}:{self.claim}:{self.url}"
        return hashlib.md5(content.encode()).hexdigest()[:8]


class EvidenceGatherer:
    """Gathers evidence from multiple sources"""
    
    def __init__(self, search_tool: Optional[WorkingResearchPipeline] = None):
        self.search_tool = search_tool or WorkingResearchPipeline()
        self.evidence_cache = {}
        
        # Source credibility database
        self.source_credibility = {
            # Academic sources
            "arxiv.org": 0.9,
            "scholar.google.com": 0.9,
            "pubmed.ncbi.nlm.nih.gov": 0.95,
            "acm.org": 0.9,
            "ieee.org": 0.9,
            
            # Industry analysts
            "gartner.com": 0.85,
            "forrester.com": 0.85,
            "mckinsey.com": 0.85,
            
            # Tech companies
            "github.com": 0.8,
            "stackoverflow.com": 0.75,
            "hackernews": 0.7,
            
            # News and blogs
            "techcrunch.com": 0.6,
            "medium.com": 0.5,
            "reddit.com": 0.4,
            
            # Default
            "default": 0.5
        }
    
    async def gather_evidence(self, 
                             requirement: str,
                             stance: str = "neutral",
                             max_sources: int = 10) -> List[Evidence]:
        """
        Gather evidence about a requirement
        
        Args:
            requirement: The requirement to research
            stance: "support", "oppose", or "neutral"
            max_sources: Maximum number of sources to gather
            
        Returns:
            List of Evidence objects
        """
        # Generate search queries based on stance
        queries = self._generate_search_queries(requirement, stance)
        
        # Gather evidence from multiple queries
        all_evidence = []
        for query in queries[:3]:  # Limit to 3 queries for speed
            results = await self._search_and_parse(query)
            evidence_list = await self._process_search_results(results, requirement)
            all_evidence.extend(evidence_list)
        
        # Deduplicate and rank evidence
        unique_evidence = self._deduplicate_evidence(all_evidence)
        ranked_evidence = sorted(unique_evidence, key=lambda e: e.total_score, reverse=True)
        
        return ranked_evidence[:max_sources]
    
    def _generate_search_queries(self, requirement: str, stance: str) -> List[str]:
        """Generate targeted search queries"""
        base_queries = []
        
        if stance == "support":
            base_queries = [
                f"{requirement} success stories",
                f"{requirement} ROI benefits",
                f"{requirement} implementation guide",
                f"why {requirement} important"
            ]
        elif stance == "oppose":
            base_queries = [
                f"{requirement} failed",
                f"{requirement} problems issues",
                f"why not {requirement}",
                f"{requirement} alternatives better"
            ]
        else:  # neutral
            base_queries = [
                f"{requirement} analysis",
                f"{requirement} pros and cons",
                f"{requirement} case study",
                f"{requirement} best practices"
            ]
        
        return base_queries
    
    async def _search_and_parse(self, query: str) -> List[Dict]:
        """Execute search and parse results"""
        try:
            # Execute search using WorkingResearchPipeline
            results = await self.search_tool.search_evidence(query, "neutral")
            
            # Results are already in the expected format from WorkingResearchPipeline
            return results if isinstance(results, list) else []
        except Exception as e:
            print(f"Search error for query '{query}': {e}")
            return []
    
    async def _process_search_results(self, 
                                     results: List[Dict],
                                     requirement: str) -> List[Evidence]:
        """Process search results into Evidence objects"""
        evidence_list = []
        
        for result in results:
            # Extract relevant fields
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            url = result.get("url", "")
            source = self._extract_domain(url)
            
            # Skip if missing critical info
            if not url or not snippet:
                continue
            
            # Create evidence object
            evidence = Evidence(
                claim=self._extract_claim(title, snippet),
                source=source,
                url=url,
                tier=self._determine_tier(source, url),
                relevance_score=self._calculate_relevance(snippet, requirement),
                recency_score=self._calculate_recency(result),
                credibility_score=self._get_source_credibility(source),
                raw_text=snippet
            )
            
            # Extract data points if present
            evidence.extracted_data = self._extract_data_points(snippet)
            
            evidence_list.append(evidence)
        
        return evidence_list
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return "unknown"
    
    def _extract_claim(self, title: str, snippet: str) -> str:
        """Extract the main claim from title and snippet"""
        # Prefer title if it's informative
        if len(title) > 20:
            return title
        
        # Otherwise, extract first sentence from snippet
        sentences = snippet.split(". ")
        return sentences[0] if sentences else snippet[:100]
    
    def _determine_tier(self, source: str, url: str) -> EvidenceTier:
        """Determine evidence tier based on source"""
        # Check for academic sources
        academic_domains = ["arxiv.org", "pubmed", "acm.org", "ieee.org", "scholar.google"]
        if any(domain in source for domain in academic_domains):
            return EvidenceTier.PLATINUM
        
        # Check for industry reports
        industry_domains = ["gartner.com", "forrester.com", "mckinsey.com", "deloitte.com"]
        if any(domain in source for domain in industry_domains):
            return EvidenceTier.GOLD
        
        # Check for tech blogs and communities
        tech_domains = ["github.com", "stackoverflow.com", "hackernews", "dev.to"]
        if any(domain in source for domain in tech_domains):
            return EvidenceTier.SILVER
        
        # Everything else is bronze
        return EvidenceTier.BRONZE
    
    def _calculate_relevance(self, text: str, requirement: str) -> float:
        """Calculate relevance score (0-1)"""
        # Simple keyword matching (could use embeddings for better results)
        requirement_words = set(requirement.lower().split())
        text_words = set(text.lower().split())
        
        if not requirement_words:
            return 0.0
        
        overlap = len(requirement_words & text_words)
        relevance = overlap / len(requirement_words)
        
        return min(1.0, relevance)
    
    def _calculate_recency(self, result: Dict) -> float:
        """Calculate recency score based on publication date"""
        # Look for date in result
        date_str = result.get("date", "")
        
        if not date_str:
            return 0.5  # Default to middle score if no date
        
        try:
            # Parse date (simplified - would need better parsing)
            from datetime import datetime
            pub_date = datetime.fromisoformat(date_str)
            days_old = (datetime.now() - pub_date).days
            
            # Score based on age
            if days_old < 30:
                return 1.0
            elif days_old < 90:
                return 0.8
            elif days_old < 365:
                return 0.6
            elif days_old < 365 * 2:
                return 0.4
            else:
                return 0.2
        except:
            return 0.5
    
    def _get_source_credibility(self, source: str) -> float:
        """Get credibility score for source"""
        for domain, score in self.source_credibility.items():
            if domain in source:
                return score
        return self.source_credibility["default"]
    
    def _extract_data_points(self, text: str) -> Dict:
        """Extract specific data points from text"""
        data_points = {}
        
        # Extract percentages
        percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', text)
        if percentages:
            data_points["percentages"] = percentages
        
        # Extract dollar amounts
        dollars = re.findall(r'\$\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*([MBK])?', text)
        if dollars:
            data_points["costs"] = dollars
        
        # Extract time periods
        time_periods = re.findall(r'(\d+)\s*(months?|years?|weeks?|days?)', text)
        if time_periods:
            data_points["timeframes"] = time_periods
        
        # Extract specific numbers
        numbers = re.findall(r'\b(\d+(?:,\d{3})*)\b', text)
        if numbers:
            data_points["metrics"] = numbers
        
        return data_points
    
    def _deduplicate_evidence(self, evidence_list: List[Evidence]) -> List[Evidence]:
        """Remove duplicate evidence based on content similarity"""
        seen_hashes = set()
        unique_evidence = []
        
        for evidence in evidence_list:
            if evidence.hash not in seen_hashes:
                seen_hashes.add(evidence.hash)
                unique_evidence.append(evidence)
        
        return unique_evidence


class EvidenceScorer:
    """Scores and ranks evidence based on multiple factors"""
    
    def __init__(self):
        self.scoring_weights = {
            "tier": 0.4,
            "relevance": 0.3,
            "recency": 0.15,
            "credibility": 0.15
        }
    
    def score_evidence_collection(self, evidence_list: List[Evidence]) -> float:
        """Score a collection of evidence"""
        if not evidence_list:
            return 0.0
        
        # Calculate weighted average of all evidence scores
        total_score = sum(e.total_score for e in evidence_list)
        return total_score / len(evidence_list)
    
    def compare_evidence(self, 
                        evidence1: Evidence,
                        evidence2: Evidence) -> str:
        """Compare two pieces of evidence and determine winner"""
        score1 = evidence1.total_score
        score2 = evidence2.total_score
        
        if score1 > score2 * 1.5:
            return "evidence1_dominates"
        elif score2 > score1 * 1.5:
            return "evidence2_dominates"
        elif score1 > score2:
            return "evidence1_wins"
        elif score2 > score1:
            return "evidence2_wins"
        else:
            return "draw"
    
    def find_counter_evidence(self,
                            evidence: Evidence,
                            evidence_pool: List[Evidence]) -> List[Evidence]:
        """Find evidence that counters a specific claim"""
        counter_evidence = []
        
        # Simple approach - look for contradicting keywords
        claim_keywords = set(evidence.claim.lower().split())
        
        for other in evidence_pool:
            # Skip same evidence
            if other.hash == evidence.hash:
                continue
            
            # Check for contradicting signals
            other_keywords = set(other.claim.lower().split())
            
            # Look for negation words
            negation_words = {"not", "no", "failed", "wrong", "false", "myth", "problem"}
            if negation_words & other_keywords and claim_keywords & other_keywords:
                counter_evidence.append(other)
        
        return counter_evidence
    
    def create_evidence_chain(self,
                            evidence_list: List[Evidence]) -> List[List[Evidence]]:
        """Create chains of supporting evidence"""
        chains = []
        used_evidence = set()
        
        for evidence in evidence_list:
            if evidence.hash in used_evidence:
                continue
            
            # Start a new chain
            chain = [evidence]
            used_evidence.add(evidence.hash)
            
            # Find supporting evidence
            for other in evidence_list:
                if other.hash in used_evidence:
                    continue
                
                # Check if evidence supports the chain
                if self._evidence_supports(other, chain):
                    chain.append(other)
                    used_evidence.add(other.hash)
            
            if len(chain) > 1:
                chains.append(chain)
        
        return chains
    
    def _evidence_supports(self, evidence: Evidence, chain: List[Evidence]) -> bool:
        """Check if evidence supports the chain"""
        # Simple keyword overlap check
        chain_keywords = set()
        for e in chain:
            chain_keywords.update(e.claim.lower().split())
        
        evidence_keywords = set(evidence.claim.lower().split())
        overlap = len(chain_keywords & evidence_keywords)
        
        return overlap >= 3  # Arbitrary threshold


class EvidenceValidator:
    """Validates evidence for quality and accuracy"""
    
    def __init__(self):
        self.validation_rules = {
            "has_source": self._check_has_source,
            "has_data": self._check_has_data,
            "not_opinion": self._check_not_pure_opinion,
            "recent_enough": self._check_recency,
            "credible_source": self._check_credibility
        }
    
    def validate_evidence(self, evidence: Evidence) -> Tuple[bool, List[str]]:
        """
        Validate a piece of evidence
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        for rule_name, rule_func in self.validation_rules.items():
            is_valid, issue = rule_func(evidence)
            if not is_valid:
                issues.append(issue)
        
        return len(issues) == 0, issues
    
    def _check_has_source(self, evidence: Evidence) -> Tuple[bool, Optional[str]]:
        """Check if evidence has a valid source"""
        if not evidence.source or evidence.source == "unknown":
            return False, "No valid source provided"
        return True, None
    
    def _check_has_data(self, evidence: Evidence) -> Tuple[bool, Optional[str]]:
        """Check if evidence contains actual data"""
        if not evidence.extracted_data:
            # Check if claim has any specifics
            has_numbers = bool(re.search(r'\d+', evidence.claim))
            has_specifics = any(word in evidence.claim.lower() 
                               for word in ["study", "report", "analysis", "data"])
            
            if not has_numbers and not has_specifics:
                return False, "No specific data or metrics provided"
        return True, None
    
    def _check_not_pure_opinion(self, evidence: Evidence) -> Tuple[bool, Optional[str]]:
        """Check if evidence is more than just opinion"""
        opinion_signals = ["i think", "i believe", "in my opinion", "i feel", "seems like"]
        claim_lower = evidence.claim.lower()
        
        if any(signal in claim_lower for signal in opinion_signals):
            return False, "Evidence appears to be opinion-based"
        return True, None
    
    def _check_recency(self, evidence: Evidence) -> Tuple[bool, Optional[str]]:
        """Check if evidence is recent enough"""
        if evidence.recency_score < 0.3:
            return False, "Evidence may be outdated"
        return True, None
    
    def _check_credibility(self, evidence: Evidence) -> Tuple[bool, Optional[str]]:
        """Check source credibility"""
        if evidence.credibility_score < 0.3:
            return False, "Source has low credibility"
        return True, None


# Evidence combo system for dramatic effects
class EvidenceCombo:
    """Manages evidence combinations and combo effects"""
    
    def __init__(self):
        self.combo_threshold = 3  # Number of supporting evidence for combo
        self.combo_multiplier = 1.5
        
    def check_for_combo(self, evidence_chain: List[Evidence]) -> Optional[Dict]:
        """Check if evidence chain creates a combo"""
        if len(evidence_chain) >= self.combo_threshold:
            # Calculate combo power
            base_score = sum(e.total_score for e in evidence_chain)
            combo_score = base_score * self.combo_multiplier
            
            return {
                "combo_size": len(evidence_chain),
                "combo_name": self._generate_combo_name(len(evidence_chain)),
                "base_score": base_score,
                "combo_score": combo_score,
                "multiplier": self.combo_multiplier,
                "evidence_chain": evidence_chain
            }
        return None
    
    def _generate_combo_name(self, size: int) -> str:
        """Generate dramatic combo names"""
        combo_names = {
            3: "Triple Evidence Strike!",
            4: "Quadruple Data Slam!",
            5: "Pentagon Evidence Formation!",
            6: "Hexagon Truth Bomb!",
            7: "Lucky Seven Evidence Chain!",
            8: "Octagon Fact Fortress!"
        }
        return combo_names.get(size, f"{size}x Evidence ULTRA COMBO!")
#built with love
