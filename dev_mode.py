#!/usr/bin/env python3
"""Development mode with intelligent mocking and minimal API usage"""

import os
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class MockMode(Enum):
    """Different levels of mocking for development"""
    FULL_MOCK = "full_mock"          # No API calls at all
    HYBRID = "hybrid"                # Mix of real and mock calls  
    MINIMAL_API = "minimal_api"      # Real API calls but optimized for cost
    PRODUCTION = "production"        # Full real API calls

@dataclass
class DevConfig:
    """Development configuration"""
    mock_mode: MockMode = MockMode.FULL_MOCK
    max_api_calls_per_session: int = 5
    use_cheapest_models: bool = True
    log_api_usage: bool = True
    simulate_delays: bool = True

class SmartMockSystem:
    """Intelligent mocking system that provides realistic responses"""
    
    def __init__(self, config: DevConfig):
        self.config = config
        self.api_call_count = 0
        
        # Pre-built response templates for common scenarios
        self.agent_responses = {
            "product_visionary": [
                "This represents a transformative opportunity! {requirement} could revolutionize how users interact with our platform.",
                "Market research shows strong demand for {requirement}. Our competitors are already moving in this direction.",
                "This aligns perfectly with our innovation roadmap. Early adoption will give us significant competitive advantage."
            ],
            "senior_architect": [
                "I've seen similar implementations fail. {requirement} introduces significant technical debt and complexity.",
                "The architecture implications are severe. This would require rebuilding core systems with questionable ROI.",
                "Based on my experience, {requirement} typically results in 2-3x cost overruns and maintenance nightmares."
            ],
            "qa_engineer": [
                "I've identified 23 potential edge cases for {requirement}. Each one needs testing and validation.",
                "This will create significant support burden. Users will be confused by the added complexity.",
                "Testing coverage for {requirement} would require 3x our current QA capacity."
            ],
            "data_analyst": [
                "Our data shows only 12% of users would regularly use {requirement}. The ROI is questionable.",
                "Similar features in our industry show 67% abandonment rates after initial launch.",
                "Cost-benefit analysis indicates {requirement} would take 18 months to break even."
            ]
        }
        
        # Evidence templates
        self.evidence_templates = {
            "academic": "Research study from MIT shows {claim} with {confidence}% confidence",
            "industry": "Gartner report indicates {claim} across {sample_size} companies", 
            "technical": "GitHub analysis reveals {claim} in {project_count} open source projects",
            "market": "Market research shows {claim} among {demographic} users"
        }
    
    def should_use_real_api(self, priority: str = "normal") -> bool:
        """Decide whether to use real API based on configuration and usage"""
        if self.config.mock_mode == MockMode.FULL_MOCK:
            return False
        elif self.config.mock_mode == MockMode.PRODUCTION:
            return True
        elif self.config.mock_mode == MockMode.MINIMAL_API:
            # Only use real API for high priority calls within limit
            return (priority == "high" and 
                   self.api_call_count < self.config.max_api_calls_per_session)
        elif self.config.mock_mode == MockMode.HYBRID:
            # 20% chance of real API call within limits
            return (random.random() < 0.2 and 
                   self.api_call_count < self.config.max_api_calls_per_session)
    
    def generate_agent_response(self, agent_type: str, requirement: str, **kwargs) -> str:
        """Generate intelligent mock responses for agents"""
        templates = self.agent_responses.get(agent_type, ["Generic response for {requirement}"])
        template = random.choice(templates)
        
        # Add some variation and context
        response = template.format(requirement=requirement, **kwargs)
        
        # Add realistic complexity based on requirement content
        if any(word in requirement.lower() for word in ["blockchain", "ai", "ml", "quantum"]):
            response += " However, the cutting-edge nature introduces significant unknowns."
        elif any(word in requirement.lower() for word in ["search", "filter", "export"]):
            response += " This is a well-understood pattern with proven implementations."
        
        return response
    
    def generate_evidence(self, requirement: str, stance: str = "neutral") -> List[Dict]:
        """Generate realistic mock evidence"""
        evidence_list = []
        
        # Generate 3-5 pieces of evidence
        for i in range(random.randint(3, 5)):
            evidence_type = random.choice(["academic", "industry", "technical", "market"])
            tier = random.choices([1, 2, 3, 4], weights=[1, 2, 3, 2])[0]  # Favor mid-tier
            
            # Generate claim based on requirement and stance
            if stance == "support":
                claims = [
                    f"shows 73% positive user response to {requirement}",
                    f"indicates 2.3x ROI improvement with {requirement}",
                    f"demonstrates successful {requirement} adoption"
                ]
            elif stance == "oppose":
                claims = [
                    f"reveals 67% failure rate for {requirement} implementations", 
                    f"shows $2M average cost overrun for {requirement}",
                    f"indicates poor user adoption of {requirement}"
                ]
            else:  # neutral
                claims = [
                    f"presents mixed results for {requirement}",
                    f"shows varying success rates for {requirement}",
                    f"highlights both benefits and risks of {requirement}"
                ]
            
            claim = random.choice(claims)
            
            evidence_list.append({
                "claim": self.evidence_templates[evidence_type].format(
                    claim=claim,
                    confidence=random.randint(60, 95),
                    sample_size=random.randint(100, 5000),
                    project_count=random.randint(50, 500),
                    demographic=random.choice(["enterprise", "SMB", "consumer"])
                ),
                "source": f"{evidence_type}-source-{i}.com",
                "url": f"https://{evidence_type}-source-{i}.com/research",
                "tier": tier,
                "relevance_score": random.uniform(0.6, 0.95),
                "credibility_score": random.uniform(0.5, 0.9),
                "recency_score": random.uniform(0.7, 1.0)
            })
        
        return evidence_list
    
    def analyze_requirement_smart(self, requirement: str, judge_type: str = "pragmatist") -> Dict:
        """Smart analysis that provides realistic results without API calls"""
        
        # Intelligent heuristics based on requirement content
        req_lower = requirement.lower()
        
        # Technology complexity assessment
        complexity_keywords = {
            "high": ["blockchain", "quantum", "metaverse", "custom database", "own cloud"],
            "medium": ["ai", "machine learning", "real-time", "microservices"],
            "low": ["search", "filter", "export", "settings", "profile"]
        }
        
        complexity = "medium"  # default
        for level, keywords in complexity_keywords.items():
            if any(keyword in req_lower for keyword in keywords):
                complexity = level
                break
        
        # Judge personality influence
        judge_biases = {
            "pragmatist": {"innovation": -0.2, "cost": 0.3, "risk": 0.4},
            "innovator": {"innovation": 0.4, "cost": -0.1, "risk": -0.2}, 
            "user_advocate": {"user_value": 0.3, "complexity": -0.3}
        }
        
        bias = judge_biases.get(judge_type, {})
        
        # Calculate base scores
        base_score = 50
        
        if complexity == "high":
            base_score -= 25
        elif complexity == "low":
            base_score += 15
        
        # Apply judge bias
        base_score += sum(bias.values()) * 10
        
        # Add some randomness
        final_score = max(10, min(95, base_score + random.uniform(-15, 15)))
        
        # Determine verdict
        if final_score >= 70:
            verdict = "APPROVED"
            alternative = None
            savings = 0
        elif final_score >= 50:
            verdict = "CONDITIONAL" 
            alternative = f"Consider MVP approach for {requirement}"
            savings = random.randint(200000, 800000)
        else:
            verdict = "REJECTED"
            alternative = self._generate_alternative(requirement)
            savings = random.randint(800000, 3000000)
        
        return {
            "requirement": requirement,
            "verdict": verdict,
            "confidence": round(final_score, 1),
            "reasoning": self._generate_reasoning(requirement, verdict, complexity),
            "alternative": alternative,
            "estimated_savings": savings,
            "evidence_summary": {
                "sources_found": random.randint(8, 24),
                "pro_evidence": random.randint(2, 8),
                "con_evidence": random.randint(3, 12),
                "neutral_evidence": random.randint(1, 4)
            },
            "complexity_assessment": complexity,
            "judge_type": judge_type,
            "mock_mode": True
        }
    
    def _generate_alternative(self, requirement: str) -> str:
        """Generate realistic alternatives"""
        alternatives = [
            f"Use existing third-party solution instead of building {requirement} from scratch",
            f"Start with manual process, automate {requirement} later if demand proves strong",
            f"Implement basic version of {requirement}, iterate based on user feedback", 
            f"Partner with established provider for {requirement} functionality",
            f"Focus on core user pain points before adding {requirement}"
        ]
        return random.choice(alternatives)
    
    def _generate_reasoning(self, requirement: str, verdict: str, complexity: str) -> str:
        """Generate realistic reasoning"""
        if verdict == "REJECTED":
            return f"Analysis shows {requirement} introduces {complexity} complexity with questionable ROI. Historical data indicates poor adoption rates for similar features."
        elif verdict == "APPROVED":
            return f"Strong evidence supports {requirement} with clear user value and manageable implementation complexity. Aligns well with strategic objectives."
        else:
            return f"Mixed evidence for {requirement}. Shows potential value but requires careful scoping to manage {complexity} complexity and implementation risks."

def create_dev_environment():
    """Set up development environment with smart mocking"""
    print("🚀 Setting up ReqDefender Development Environment")
    print("=" * 50)
    
    # Check what's available
    has_openai = os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your_openai_api_key_here"
    has_anthropic = os.getenv("ANTHROPIC_API_KEY") and os.getenv("ANTHROPIC_API_KEY") != "your_anthropic_api_key_here"
    
    print("API Key Status:")
    print(f"  OpenAI: {'✅ Available' if has_openai else '❌ Not configured'}")
    print(f"  Anthropic: {'✅ Available' if has_anthropic else '❌ Not configured'}")
    
    # Recommend development mode
    if not has_openai and not has_anthropic:
        recommended_mode = MockMode.FULL_MOCK
        print("\n💡 Recommended: FULL_MOCK mode (no API keys needed)")
    elif has_openai or has_anthropic:
        recommended_mode = MockMode.MINIMAL_API
        print("\n💡 Recommended: MINIMAL_API mode (test with few real calls)")
    
    print("\nAvailable modes:")
    print("  1. FULL_MOCK - No API calls, intelligent simulation")
    print("  2. MINIMAL_API - Max 5 real calls per session") 
    print("  3. HYBRID - Mix of real and mock calls")
    print("  4. PRODUCTION - Full real API usage")
    
    choice = input(f"\nSelect mode (1-4) [default: {recommended_mode.value[0]}]: ").strip()
    
    mode_map = {
        "1": MockMode.FULL_MOCK,
        "2": MockMode.MINIMAL_API, 
        "3": MockMode.HYBRID,
        "4": MockMode.PRODUCTION,
        "": recommended_mode
    }
    
    selected_mode = mode_map.get(choice, recommended_mode)
    
    config = DevConfig(
        mock_mode=selected_mode,
        max_api_calls_per_session=5,
        use_cheapest_models=True,
        log_api_usage=True
    )
    
    print(f"\n✅ Development environment configured: {selected_mode.value.upper()}")
    
    return SmartMockSystem(config)

if __name__ == "__main__":
    # Demo the development system
    mock_system = create_dev_environment()
    
    print("\n🧪 Testing Smart Mock System")
    print("-" * 30)
    
    test_requirements = [
        "Add blockchain to our todo app",
        "Implement search functionality", 
        "Build AI-powered recommendations",
        "Add user profile settings"
    ]
    
    for req in test_requirements:
        result = mock_system.analyze_requirement_smart(req)
        print(f"\n📋 {req}")
        print(f"   Verdict: {result['verdict']} ({result['confidence']}%)")
        print(f"   Complexity: {result['complexity_assessment']}")
        if result.get('estimated_savings'):
            print(f"   Savings: ${result['estimated_savings']:,}")
        if result.get('alternative'):
            print(f"   Alternative: {result['alternative'][:60]}...")
    
    print(f"\n🎉 Smart mock system ready! API calls used: {mock_system.api_call_count}")
#built with love
