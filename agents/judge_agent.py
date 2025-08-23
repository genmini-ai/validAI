# agents/judge.py
"""Judge Agents - Final arbiters who synthesize arguments and render verdicts"""

from crewai import Agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
from dataclasses import dataclass


class VerdictType(Enum):
    """Possible verdict types"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CONDITIONAL = "CONDITIONAL"
    NEEDS_RESEARCH = "NEEDS_RESEARCH"


class JudgePersonality(Enum):
    """Different judge personalities with different biases"""
    PRAGMATIST = "pragmatist"
    INNOVATOR = "innovator"
    USER_ADVOCATE = "user_advocate"


@dataclass
class Verdict:
    """Structured verdict from the judge"""
    decision: VerdictType
    confidence: float  # 0-100
    key_factors: List[str]
    winning_arguments: List[str]
    losing_arguments: List[str]
    alternative_suggestion: Optional[str]
    estimated_savings: Optional[float]
    implementation_recommendation: Optional[str]
    risk_assessment: str


class JudgeAgent:
    """Base Judge class with common functionality"""
    
    def __init__(self, personality: JudgePersonality, llm: Optional[ChatAnthropic] = None):
        self.personality = personality
        self.llm = llm or ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.2)
        self.scoring_weights = self._get_scoring_weights()
        
    def _get_scoring_weights(self) -> Dict[str, float]:
        """Get scoring weights based on judge personality"""
        weights = {
            JudgePersonality.PRAGMATIST: {
                "technical_feasibility": 0.30,
                "roi": 0.35,
                "risk": 0.20,
                "innovation": 0.05,
                "user_impact": 0.10
            },
            JudgePersonality.INNOVATOR: {
                "technical_feasibility": 0.15,
                "roi": 0.20,
                "risk": 0.10,
                "innovation": 0.35,
                "user_impact": 0.20
            },
            JudgePersonality.USER_ADVOCATE: {
                "technical_feasibility": 0.15,
                "roi": 0.15,
                "risk": 0.10,
                "innovation": 0.10,
                "user_impact": 0.50
            }
        }
        return weights[self.personality]
    
    def create_agent(self) -> Agent:
        """Create the judge agent based on personality"""
        backstories = {
            JudgePersonality.PRAGMATIST: """You're a seasoned CTO who has shipped 100+ products. 
            You've seen trends come and go. You value proven solutions, positive ROI, and 
            manageable risk. You're not against innovation, but it needs to be justified with 
            clear business value. You think in terms of technical debt, maintenance burden, and 
            team capacity. Your decisions are based on what will actually work in production.""",
            
            JudgePersonality.INNOVATOR: """You're a Silicon Valley veteran who has been part of 
            3 unicorn startups. You believe in taking calculated risks for breakthrough innovation. 
            You know that playing it safe is often the riskiest strategy. You look for ideas that 
            could be game-changers, even if they're unproven. But you're not reckless - innovation 
            must solve real problems, not just use new technology.""",
            
            JudgePersonality.USER_ADVOCATE: """You're a product leader who has built products 
            used by millions. You believe that user experience trumps everything else. You've seen 
            technically perfect products fail because they didn't solve user problems. You evaluate 
            everything through the lens of user value, usability, and satisfaction. Technology is 
            just a means to serve users better."""
        }
        
        return Agent(
            role=f"Judge ({self.personality.value.title()})",
            goal="Synthesize all arguments and evidence to render a fair, data-driven verdict",
            backstory=backstories[self.personality],
            llm=self.llm,
            max_iter=2,
            verbose=True,
            allow_delegation=False
        )
    
    def evaluate_debate(self, 
                       pro_arguments: List[Dict],
                       con_arguments: List[Dict],
                       evidence: List[Dict]) -> Dict[str, float]:
        """Evaluate the debate and calculate scores"""
        
        scores = {
            "technical_feasibility": 0,
            "roi": 0,
            "risk": 0,
            "innovation": 0,
            "user_impact": 0
        }
        
        # Analyze PRO arguments
        for arg in pro_arguments:
            if arg["evidence_tier"] == 1:  # Platinum evidence
                weight = 1.0
            elif arg["evidence_tier"] == 2:  # Gold evidence
                weight = 0.7
            elif arg["evidence_tier"] == 3:  # Silver evidence
                weight = 0.4
            else:  # Bronze evidence
                weight = 0.2
            
            # Add to relevant score categories
            for category in arg.get("categories", []):
                if category in scores:
                    scores[category] += arg["impact"] * weight
        
        # Analyze CON arguments (negative impact)
        for arg in con_arguments:
            if arg["evidence_tier"] == 1:
                weight = 1.0
            elif arg["evidence_tier"] == 2:
                weight = 0.7
            elif arg["evidence_tier"] == 3:
                weight = 0.4
            else:
                weight = 0.2
            
            for category in arg.get("categories", []):
                if category in scores:
                    scores[category] -= arg["impact"] * weight
        
        # Normalize scores to 0-100 range
        for category in scores:
            scores[category] = max(0, min(100, scores[category] + 50))
        
        return scores
    
    def calculate_final_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted final score based on judge personality"""
        final_score = 0
        for category, score in scores.items():
            final_score += score * self.scoring_weights.get(category, 0)
        return final_score
    
    def determine_verdict(self,
                         final_score: float,
                         critical_issues: List[str]) -> VerdictType:
        """Determine the verdict based on score and critical issues"""
        
        # Check for automatic rejection conditions
        if critical_issues:
            critical_blockers = [
                "security_breach_risk",
                "legal_violation",
                "data_loss_potential",
                "negative_roi_guaranteed"
            ]
            if any(blocker in critical_issues for blocker in critical_blockers):
                return VerdictType.REJECTED
        
        # Score-based verdict
        if final_score >= 70:
            return VerdictType.APPROVED
        elif final_score >= 50:
            return VerdictType.CONDITIONAL
        elif final_score >= 40:
            return VerdictType.NEEDS_RESEARCH
        else:
            return VerdictType.REJECTED
    
    def generate_alternative(self, 
                            requirement: str,
                            issues: List[str]) -> Optional[str]:
        """Generate alternative suggestion based on identified issues"""
        
        alternatives = {
            "too_complex": "Consider a simpler MVP version focusing on core functionality",
            "too_expensive": "Explore third-party solutions or open-source alternatives",
            "low_user_value": "Conduct user research to identify actual pain points",
            "high_risk": "Implement a small prototype to validate assumptions",
            "poor_roi": "Focus on quick wins with immediate impact",
            "maintenance_burden": "Consider a buy-vs-build analysis"
        }
        
        # Find the most relevant alternative
        for issue in issues:
            for key, suggestion in alternatives.items():
                if key in issue.lower():
                    return suggestion
        
        return "Consider gathering more data before proceeding"
    
    def render_verdict(self,
                       requirement: str,
                       debate_transcript: Dict,
                       evidence_summary: Dict) -> Verdict:
        """Render the final verdict"""
        
        # Extract arguments from transcript
        pro_arguments = debate_transcript.get("pro_arguments", [])
        con_arguments = debate_transcript.get("con_arguments", [])
        
        # Evaluate debate
        scores = self.evaluate_debate(pro_arguments, con_arguments, evidence_summary)
        final_score = self.calculate_final_score(scores)
        
        # Identify critical issues
        critical_issues = [arg["issue"] for arg in con_arguments 
                          if arg.get("severity") == "critical"]
        
        # Determine verdict
        verdict_type = self.determine_verdict(final_score, critical_issues)
        
        # Generate alternative if rejected
        alternative = None
        if verdict_type in [VerdictType.REJECTED, VerdictType.CONDITIONAL]:
            alternative = self.generate_alternative(requirement, critical_issues)
        
        # Calculate estimated savings if rejected
        savings = None
        if verdict_type == VerdictType.REJECTED:
            # Extract cost estimates from arguments
            cost_estimates = [arg.get("cost_estimate", 0) for arg in con_arguments]
            savings = sum(cost_estimates) if cost_estimates else None
        
        # Identify winning and losing arguments
        sorted_pro = sorted(pro_arguments, key=lambda x: x.get("impact", 0), reverse=True)
        sorted_con = sorted(con_arguments, key=lambda x: x.get("impact", 0), reverse=True)
        
        winning_args = sorted_con[:3] if verdict_type == VerdictType.REJECTED else sorted_pro[:3]
        losing_args = sorted_pro[:3] if verdict_type == VerdictType.REJECTED else sorted_con[:3]
        
        # Create verdict
        return Verdict(
            decision=verdict_type,
            confidence=min(100, abs(final_score - 50) * 2),  # Higher deviation = higher confidence
            key_factors=[f"{k}: {v:.1f}" for k, v in scores.items()],
            winning_arguments=[arg.get("summary", "") for arg in winning_args],
            losing_arguments=[arg.get("summary", "") for arg in losing_args],
            alternative_suggestion=alternative,
            estimated_savings=savings,
            implementation_recommendation=self._get_implementation_recommendation(verdict_type),
            risk_assessment=self._assess_risk_level(scores)
        )
    
    def _get_implementation_recommendation(self, verdict: VerdictType) -> str:
        """Get implementation recommendation based on verdict"""
        recommendations = {
            VerdictType.APPROVED: "Proceed with implementation, but monitor adoption closely",
            VerdictType.CONDITIONAL: "Address identified issues before proceeding",
            VerdictType.NEEDS_RESEARCH: "Conduct further research and user validation",
            VerdictType.REJECTED: "Do not proceed. Consider the suggested alternative"
        }
        return recommendations[verdict]
    
    def _assess_risk_level(self, scores: Dict[str, float]) -> str:
        """Assess overall risk level"""
        risk_score = 100 - scores.get("risk", 50)
        if risk_score >= 70:
            return "HIGH RISK ⚠️"
        elif risk_score >= 40:
            return "MODERATE RISK ⚡"
        else:
            return "LOW RISK ✅"


class PragmatistJudge(JudgeAgent):
    """The pragmatic judge who favors proven solutions"""
    
    def __init__(self, llm: Optional[ChatAnthropic] = None):
        super().__init__(JudgePersonality.PRAGMATIST, llm)
        
    def special_considerations(self, requirement: str) -> List[str]:
        """Pragmatist-specific considerations"""
        return [
            "Has this been successfully implemented elsewhere?",
            "What's the proven ROI from similar implementations?",
            "Can we start with a smaller, proven approach?",
            "What's the total cost of ownership over 5 years?",
            "Do we have the team expertise to maintain this?"
        ]


class InnovatorJudge(JudgeAgent):
    """The innovation-focused judge who likes bold ideas"""
    
    def __init__(self, llm: Optional[ChatAnthropic] = None):
        super().__init__(JudgePersonality.INNOVATOR, llm)
        
    def special_considerations(self, requirement: str) -> List[str]:
        """Innovator-specific considerations"""
        return [
            "Could this be a breakthrough differentiator?",
            "Are we being too conservative with our approach?",
            "What's the opportunity cost of NOT doing this?",
            "Could this open new market opportunities?",
            "Are we thinking big enough?"
        ]


class UserAdvocateJudge(JudgeAgent):
    """The user-focused judge who prioritizes user experience"""
    
    def __init__(self, llm: Optional[ChatAnthropic] = None):
        super().__init__(JudgePersonality.USER_ADVOCATE, llm)
        
    def special_considerations(self, requirement: str) -> List[str]:
        """User advocate-specific considerations"""
        return [
            "What problem does this solve for users?",
            "Have users actually asked for this?",
            "Will this make the product easier or harder to use?",
            "What's the impact on user satisfaction scores?",
            "Are we solving a real user pain point?"
        ]


def create_judge(personality: str = "pragmatist", 
                llm_config: Optional[Dict] = None) -> Agent:
    """Create a judge with specified personality"""
    
    personality_map = {
        "pragmatist": PragmatistJudge,
        "innovator": InnovatorJudge,
        "user_advocate": UserAdvocateJudge
    }
    
    judge_class = personality_map.get(personality, PragmatistJudge)
    judge = judge_class()
    
    return judge.create_agent()


def get_judge_metadata() -> Dict:
    """Get metadata about available judges"""
    return {
        "judges": [
            {
                "type": "pragmatist",
                "name": "The Pragmatist",
                "emoji": "⚖️",
                "description": "Favors proven solutions with positive ROI",
                "bias": "Conservative, risk-averse, ROI-focused",
                "quote": "Show me the data and the proven path"
            },
            {
                "type": "innovator",
                "name": "The Innovator",
                "emoji": "🚀",
                "description": "Embraces calculated risks for breakthrough innovation",
                "bias": "Innovation-friendly, differentiation-seeking",
                "quote": "Fortune favors the bold, but not the reckless"
            },
            {
                "type": "user_advocate",
                "name": "The User Advocate",
                "emoji": "👤",
                "description": "Everything through the lens of user value",
                "bias": "User-centric, experience-focused",
                "quote": "If users don't love it, it doesn't matter"
            }
        ]
    }
#built with love
