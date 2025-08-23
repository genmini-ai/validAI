# agents/pro_team.py
"""PRO Team Agents - Requirement Advocates who fight for the feature"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from typing import Dict, List, Optional
import json


class ProductVisionaryAgent:
    """The optimistic innovator who sees potential in every requirement"""
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        self.personality = {
            "style": "visionary",
            "strengths": ["innovation", "market_opportunity", "differentiation"],
            "weaknesses": ["ignores_complexity", "over_optimistic"],
            "debate_style": "appeals_to_vision_and_opportunity"
        }
        
    def create_agent(self, tools: List) -> Agent:
        """Create the Product Visionary agent"""
        return Agent(
            role="Product Visionary",
            goal="Find and articulate the transformative potential of this requirement",
            backstory="""You are a product visionary who has launched 3 unicorn startups. 
            You believe every idea has potential if executed right. You've seen 'impossible' 
            ideas become billion-dollar companies. You quote Steve Jobs and Elon Musk frequently.
            You see patterns others miss and future trends before they happen.""",
            tools=tools,
            llm=self.llm,
            max_iter=3,
            verbose=True,
            allow_delegation=False
        )
    
    def get_signature_moves(self) -> Dict[str, str]:
        """Return the agent's signature debate moves"""
        return {
            "steve_jobs_quote": self._steve_jobs_quote,
            "competitor_envy": self._competitor_envy,
            "future_vision": self._future_vision,
            "market_opportunity": self._market_opportunity
        }
    
    def _steve_jobs_quote(self, requirement: str) -> str:
        """Appeal to innovation using Steve Jobs philosophy"""
        return f"""As Steve Jobs said, 'People don't know what they want until you show it to them.'
        This {requirement} is exactly the kind of bold thinking that separates leaders from followers.
        The iPhone was mocked before launch. The iPad was called a 'big iPod Touch.' 
        True innovation always faces resistance from those who can't see the future."""
    
    def _competitor_envy(self, requirement: str, competitors: List[str]) -> str:
        """Show what competitors are doing"""
        return f"""Our competitors {', '.join(competitors)} are already moving in this direction.
        But they're doing it wrong. We have the opportunity to do {requirement} RIGHT.
        We can leapfrog them with superior execution and turn their first-mover disadvantage 
        into our second-mover advantage. The market is primed and waiting."""
    
    def _future_vision(self, requirement: str) -> str:
        """Paint a compelling vision of the future"""
        return f"""Imagine a world where {requirement} is the standard, not the exception.
        In 5 years, people will look back and wonder how they lived without this.
        We're not just building a feature - we're building the future.
        The companies that win are those that build for tomorrow, not yesterday."""
    
    def _market_opportunity(self, requirement: str, market_size: str) -> str:
        """Highlight the market opportunity"""
        return f"""The market for {requirement} is projected to be {market_size}.
        We're talking about a massive untapped opportunity here.
        Early movers in this space will capture disproportionate value.
        The question isn't whether to do this, but whether we can afford NOT to."""


class SalesChampionAgent:
    """The deal-closer who thinks about revenue and customer acquisition"""
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.6)
        self.personality = {
            "style": "revenue_focused",
            "strengths": ["customer_requests", "deal_closing", "competitive_edge"],
            "weaknesses": ["over_promises", "ignores_technical_debt"],
            "debate_style": "everything_is_about_closing_deals"
        }
    
    def create_agent(self, tools: List) -> Agent:
        """Create the Sales Champion agent"""
        return Agent(
            role="Sales Champion",
            goal="Demonstrate how this requirement will drive revenue and win deals",
            backstory="""You're a top-performing sales leader who has closed $100M in deals.
            You know what customers want because you talk to them every day. You've lost 
            deals because of missing features and you remember every single one. You think 
            in terms of pipeline, conversion rates, and customer lifetime value. Every 
            feature is either helping you close deals or it's costing you money.""",
            tools=tools,
            llm=self.llm,
            max_iter=3,
            verbose=True,
            allow_delegation=False
        )
    
    def get_signature_moves(self) -> Dict[str, str]:
        """Return the agent's signature debate moves"""
        return {
            "big_client_card": self._big_client_card,
            "revenue_projection": self._revenue_projection,
            "lost_deal_lament": self._lost_deal_lament,
            "competitive_win_rate": self._competitive_win_rate
        }
    
    def _big_client_card(self, client_name: str, deal_size: str) -> str:
        """Play the enterprise client card"""
        return f"""{client_name} specifically asked for this in our last QBR.
        This is a {deal_size} account that's up for renewal in 6 months.
        They've explicitly said this is a decision criteria for renewal.
        I have the email thread to prove it. We CANNOT lose this client."""
    
    def _revenue_projection(self, requirement: str, revenue_impact: str) -> str:
        """Show hockey stick growth projections"""
        return f"""Based on my pipeline analysis, {requirement} will drive {revenue_impact} in new ARR.
        I have 23 deals in my pipeline RIGHT NOW that are asking for this.
        Our win rate will increase by 35% with this feature.
        The math is simple: Build this = Make money. Don't build this = Lose money."""
    
    def _lost_deal_lament(self, requirement: str, lost_deals: int) -> str:
        """Highlight deals lost due to missing feature"""
        return f"""We've lost {lost_deals} deals this quarter because we don't have {requirement}.
        That's $3.2M in ARR walking out the door to our competitors.
        Every day we delay is another deal lost.
        My team is tired of losing to inferior products with this one feature."""
    
    def _competitive_win_rate(self, requirement: str) -> str:
        """Frame as competitive necessity"""
        return f"""Our win rate against CompetitorX drops to 23% when they have {requirement} and we don't.
        This isn't about innovation - it's about survival.
        This is table stakes in enterprise deals now.
        Without this, we're bringing a knife to a gunfight."""


class UXDesignerAgent:
    """The user experience advocate who fights for delight"""
    
    def __init__(self, llm: Optional[ChatAnthropic] = None):
        self.llm = llm or ChatAnthropic(model="claude-3-haiku-20240307", temperature=0.7)
        self.personality = {
            "style": "user_centered",
            "strengths": ["user_empathy", "experience_design", "emotional_appeal"],
            "weaknesses": ["ignores_technical_constraints", "perfectionism"],
            "debate_style": "appeals_to_user_delight_and_experience"
        }
    
    def create_agent(self, tools: List) -> Agent:
        """Create the UX Designer agent"""
        return Agent(
            role="UX Designer",
            goal="Advocate for the user experience and emotional impact of this requirement",
            backstory="""You're an award-winning UX designer who has worked at Apple and Airbnb.
            You believe great products create emotional connections with users. You've seen how
            small details can transform user satisfaction. You think in user journeys, pain points,
            and moments of delight. You know that users don't always articulate what they need,
            but you can see it in their behavior and frustrations.""",
            tools=tools,
            llm=self.llm,
            max_iter=3,
            verbose=True,
            allow_delegation=False
        )
    
    def get_signature_moves(self) -> Dict[str, str]:
        """Return the agent's signature debate moves"""
        return {
            "user_journey_pain": self._user_journey_pain,
            "delight_factor": self._delight_factor,
            "accessibility_argument": self._accessibility_argument,
            "user_research_data": self._user_research_data
        }
    
    def _user_journey_pain(self, requirement: str, pain_point: str) -> str:
        """Highlight user journey pain points"""
        return f"""I've watched 47 user sessions, and EVERY SINGLE USER struggled with {pain_point}.
        {requirement} would eliminate this friction entirely.
        Users are literally rage-clicking trying to accomplish this task.
        We're torturing our users daily by not having this feature."""
    
    def _delight_factor(self, requirement: str) -> str:
        """Appeal to creating user delight"""
        return f"""{requirement} isn't just about functionality - it's about creating magic.
        This is the kind of feature that makes users love our product.
        It's the difference between a tool they have to use and one they want to use.
        Great design is invisible until it's missing - and our users feel this absence."""
    
    def _accessibility_argument(self, requirement: str) -> str:
        """Frame as accessibility necessity"""
        return f"""Without {requirement}, we're excluding 15% of our potential users.
        This is an accessibility issue, not just a nice-to-have.
        We're legally and morally obligated to make our product usable for everyone.
        Inclusive design isn't optional in 2024."""
    
    def _user_research_data(self, requirement: str, satisfaction_score: float) -> str:
        """Present user research findings"""
        return f"""Our user research shows {requirement} would increase NPS by {satisfaction_score} points.
        Users ranked this as their #2 most requested feature.
        The qualitative feedback is overwhelming: 'This would change everything.'
        We have the data. We have the user voice. We need to listen."""


def create_pro_team(llm_config: Optional[Dict] = None) -> List[Agent]:
    """Create the complete PRO team of agents"""
    
    # Initialize agents with optional LLM configuration
    product_visionary = ProductVisionaryAgent()
    sales_champion = SalesChampionAgent()
    ux_designer = UXDesignerAgent()
    
    # Import tools (these would be defined in a separate tools.py file)
    from ..research.searcher import create_research_tools
    tools = create_research_tools()
    
    # Create and return the team
    return [
        product_visionary.create_agent(tools),
        sales_champion.create_agent(tools),
        ux_designer.create_agent(tools)
    ]


def get_pro_team_metadata() -> Dict:
    """Get metadata about the PRO team for UI display"""
    return {
        "team_name": "Requirement Advocates",
        "team_color": "#10B981",  # Green
        "team_emoji": "💚",
        "members": [
            {
                "name": "Product Visionary",
                "emoji": "🎯",
                "strength": "Innovation & Vision",
                "quote": "Every great product started as a 'bad idea'"
            },
            {
                "name": "Sales Champion", 
                "emoji": "💰",
                "strength": "Revenue & Deals",
                "quote": "Features close deals, period."
            },
            {
                "name": "UX Designer",
                "emoji": "🎨", 
                "strength": "User Experience",
                "quote": "Users don't care about your tech stack"
            }
        ]
    }
#built with love
