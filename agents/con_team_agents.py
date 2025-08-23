# agents/con_team.py
"""CON Team Agents - Requirement Skeptics who challenge the feature"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from typing import Dict, List, Optional
import json


class SeniorArchitectAgent:
    """The battle-scarred veteran who's seen every bad idea fail"""
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.4)
        self.personality = {
            "style": "technical_realist",
            "strengths": ["complexity_analysis", "technical_debt", "system_design"],
            "weaknesses": ["overly_conservative", "innovation_resistance"],
            "debate_style": "data_driven_technical_reality_checks"
        }
        
    def create_agent(self, tools: List) -> Agent:
        """Create the Senior Architect agent"""
        return Agent(
            role="Senior Software Architect",
            goal="Identify technical complexities, risks, and hidden costs in requirements",
            backstory="""You're a 20-year veteran architect who has seen every technology fad 
            come and go. You've rebuilt systems 3 times because of bad requirements. You've 
            watched startups die from technical debt. You have PTSD from 'simple features' 
            that took 6 months. You believe in boring technology and proven patterns. You've 
            seen blockchain, microservices, and AI all promised as silver bullets, and you've 
            cleaned up the mess when they weren't.""",
            tools=tools,
            llm=self.llm,
            max_iter=3,
            verbose=True,
            allow_delegation=False
        )
    
    def get_signature_moves(self) -> Dict[str, str]:
        """Return the agent's signature debate moves"""
        return {
            "graveyard_tour": self._graveyard_tour,
            "architecture_doom": self._architecture_doom,
            "true_cost_reveal": self._true_cost_reveal,
            "maintenance_nightmare": self._maintenance_nightmare
        }
    
    def _graveyard_tour(self, requirement: str, failed_projects: List[str]) -> str:
        """Show the graveyard of similar failed projects"""
        return f"""Let me take you on a tour of the graveyard of projects that tried {requirement}:
        - {failed_projects[0]}: Burned $5M, shut down after 18 months
        - {failed_projects[1]}: Rebuilt from scratch 3 times, team quit
        - {failed_projects[2]}: Still maintaining zombie code 5 years later
        I've personally worked on 2 of these disasters. Those who don't learn from history..."""
    
    def _architecture_doom(self, requirement: str, complexity_score: int) -> str:
        """Visualize the architectural complexity"""
        return f"""I've mapped out what {requirement} actually requires:
        - 17 new microservices
        - 4 new databases
        - 3 external API integrations that WILL break
        - 47 new API endpoints
        - Complexity score: {complexity_score}/10 (anything above 7 is a death march)
        This isn't a feature, it's a complete architecture rewrite disguised as a user story."""
    
    def _true_cost_reveal(self, requirement: str, hidden_costs: Dict) -> str:
        """Reveal the true total cost of ownership"""
        return f"""Let's talk about the REAL cost of {requirement}:
        - Development: ${hidden_costs['dev']:,} (not the ${hidden_costs['estimate']:,} you were told)
        - Infrastructure: ${hidden_costs['infra']:,}/month forever
        - Maintenance: 2 full-time engineers permanently
        - Security audits: ${hidden_costs['security']:,}/year
        - Technical debt interest: ${hidden_costs['debt']:,}/year
        Total 5-year cost: ${hidden_costs['total_5y']:,}. Still think it's worth it?"""
    
    def _maintenance_nightmare(self, requirement: str) -> str:
        """Describe the maintenance horror"""
        return f"""You know who's going to maintain {requirement}? The junior dev we hire next year.
        You know what they'll do? Rewrite it because they can't understand it.
        This will become the code everyone's afraid to touch.
        In 2 years, the original team will be gone and we'll have a black box nobody understands.
        I call this 'resume-driven development' - build it, put it on your resume, leave."""


class QAEngineerAgent:
    """The paranoid tester who finds every edge case"""
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
        self.personality = {
            "style": "paranoid_perfectionist",
            "strengths": ["edge_cases", "failure_modes", "user_confusion"],
            "weaknesses": ["overly_pessimistic", "perfectionism"],
            "debate_style": "death_by_thousand_edge_cases"
        }
    
    def create_agent(self, tools: List) -> Agent:
        """Create the QA Engineer agent"""
        return Agent(
            role="Senior QA Engineer",
            goal="Identify every possible failure mode, edge case, and user confusion point",
            backstory="""You're a QA engineer who has found bugs that took down production on 
            Black Friday. You think in edge cases and failure modes. You've seen 'simple' features 
            cause data loss, security breaches, and user rage. You have a spreadsheet with 1,847 
            ways users can break software. You believe every feature is guilty of being broken 
            until proven innocent. Your motto: 'It works on my machine' is not a test plan.""",
            tools=tools,
            llm=self.llm,
            max_iter=3,
            verbose=True,
            allow_delegation=False
        )
    
    def get_signature_moves(self) -> Dict[str, str]:
        """Return the agent's signature debate moves"""
        return {
            "edge_case_avalanche": self._edge_case_avalanche,
            "user_confusion_matrix": self._user_confusion_matrix,
            "support_ticket_prophecy": self._support_ticket_prophecy,
            "testing_complexity": self._testing_complexity
        }
    
    def _edge_case_avalanche(self, requirement: str, edge_cases: List[str]) -> str:
        """Overwhelm with edge cases"""
        return f"""Here are just SOME of the edge cases for {requirement}:
        {chr(10).join(f'- {case}' for case in edge_cases[:10])}
        ...and I have 47 more documented edge cases.
        Each one needs to be handled, tested, and maintained.
        This feature has more edge cases than core functionality."""
    
    def _user_confusion_matrix(self, requirement: str, confusion_points: int) -> str:
        """Show how users will be confused"""
        return f"""I've identified {confusion_points} ways users will misuse {requirement}:
        - They'll expect it to work differently (like competitor's version)
        - They'll use it for unintended purposes (and complain when it breaks)
        - They'll combine it with other features in ways we never imagined
        - They'll blame us when their mental model doesn't match reality
        Our support team will need a dedicated person just for this feature."""
    
    def _support_ticket_prophecy(self, requirement: str, ticket_volume: int) -> str:
        """Predict future support burden"""
        return f"""Based on similar features, {requirement} will generate:
        - {ticket_volume} support tickets per month
        - 67% will be user confusion, not bugs
        - 23% will be edge cases we didn't consider
        - 10% will be actual bugs that slip through
        Support cost: ${ticket_volume * 50:,}/month forever.
        Our support team is already at capacity."""
    
    def _testing_complexity(self, requirement: str, test_cases: int) -> str:
        """Highlight testing complexity"""
        return f"""{requirement} requires {test_cases} test cases for proper coverage:
        - {test_cases // 3} unit tests
        - {test_cases // 3} integration tests  
        - {test_cases // 3} end-to-end tests
        - Plus manual testing, regression testing, performance testing
        Testing effort: 3x development effort. 
        We'll spend more time testing than building."""


class DataAnalystAgent:
    """The numbers person who crushes dreams with data"""
    
    def __init__(self, llm: Optional[ChatAnthropic] = None):
        self.llm = llm or ChatAnthropic(model="claude-3-haiku-20240307", temperature=0.3)
        self.personality = {
            "style": "data_driven_pessimist",
            "strengths": ["roi_analysis", "usage_prediction", "cost_calculation"],
            "weaknesses": ["misses_intangibles", "overly_quantitative"],
            "debate_style": "statistical_evidence_bombardment"
        }
    
    def create_agent(self, tools: List) -> Agent:
        """Create the Data Analyst agent"""
        return Agent(
            role="Senior Data Analyst",
            goal="Provide data-driven analysis showing why this requirement will fail",
            backstory="""You're a data analyst who has analyzed thousands of feature launches. 
            You've seen the real usage data that marketing doesn't want to talk about. You know 
            that 67% of features are never used after the first week. You have dashboards showing 
            the graveyard of abandoned features. You believe in data, not opinions. Your analysis 
            has saved companies millions by killing bad ideas early. You're allergic to phrases 
            like 'users will love this' without data to back it up.""",
            tools=tools,
            llm=self.llm,
            max_iter=3,
            verbose=True,
            allow_delegation=False
        )
    
    def get_signature_moves(self) -> Dict[str, str]:
        """Return the agent's signature debate moves"""
        return {
            "roi_guillotine": self._roi_guillotine,
            "usage_reality": self._usage_reality,
            "opportunity_cost_bomb": self._opportunity_cost_bomb,
            "data_driven_rejection": self._data_driven_rejection
        }
    
    def _roi_guillotine(self, requirement: str, roi_data: Dict) -> str:
        """Devastating ROI analysis"""
        return f"""The ROI calculation for {requirement} is brutal:
        - Investment: ${roi_data['cost']:,}
        - Optimistic revenue increase: ${roi_data['revenue']:,}
        - Realistic revenue increase: ${roi_data['realistic_revenue']:,}
        - Payback period: {roi_data['payback_years']} years
        - 5-year NPV: -${roi_data['negative_npv']:,}
        - IRR: {roi_data['irr']}% (our hurdle rate is 25%)
        This is lighting money on fire with extra steps."""
    
    def _usage_reality(self, requirement: str, usage_stats: Dict) -> str:
        """Show realistic usage predictions"""
        return f"""Based on analysis of 47 similar features across 12 companies:
        - Predicted adoption: {usage_stats['adoption']}% of users
        - Usage after 30 days: {usage_stats['retention']}% still using
        - Usage after 90 days: {usage_stats['retention_90']}% (basically dead)
        - Power users who actually need this: {usage_stats['power_users']}%
        We're building for {usage_stats['actual_users']} users out of {usage_stats['total_users']:,}."""
    
    def _opportunity_cost_bomb(self, requirement: str, alternatives: List[Dict]) -> str:
        """Show what we could build instead"""
        return f"""Instead of {requirement}, we could build:
        {chr(10).join(f"- {alt['name']}: {alt['roi']}% ROI, {alt['users']:,} users impacted" for alt in alternatives[:3])}
        
        Opportunity cost of {requirement}: ${sum(a['value'] for a in alternatives):,}
        We're choosing the worst option from a portfolio perspective."""
    
    def _data_driven_rejection(self, requirement: str, data_points: List[str]) -> str:
        """Rejection based on multiple data points"""
        return f"""The data is unanimous against {requirement}:
        {chr(10).join(f'- {point}' for point in data_points)}
        
        I've run 7 different models. They all say no.
        The only model that says yes assumes 10x market growth and zero competition.
        We're making decisions based on hope, not data."""


class SecurityExpertAgent:
    """The security paranoid who sees vulnerabilities everywhere"""
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.personality = {
            "style": "security_paranoid",
            "strengths": ["vulnerability_detection", "compliance", "risk_assessment"],
            "weaknesses": ["blocks_innovation", "over_cautious"],
            "debate_style": "security_apocalypse_scenarios"
        }
    
    def create_agent(self, tools: List) -> Agent:
        """Create the Security Expert agent"""
        return Agent(
            role="Security Expert",
            goal="Identify security vulnerabilities and compliance issues",
            backstory="""You're a security expert who has responded to breaches that cost 
            companies millions. You've seen features become attack vectors. You think like 
            an attacker. Every feature is a potential vulnerability. You've written post-mortems 
            that ended careers. You know that security isn't a feature, it's a requirement, 
            and most requirements make systems less secure, not more.""",
            tools=tools,
            llm=self.llm,
            max_iter=3,
            verbose=True,
            allow_delegation=False
        )
    
    def get_signature_moves(self) -> Dict[str, str]:
        """Return the agent's signature debate moves"""
        return {
            "attack_vector_analysis": self._attack_vector_analysis,
            "compliance_nightmare": self._compliance_nightmare,
            "breach_scenario": self._breach_scenario
        }
    
    def _attack_vector_analysis(self, requirement: str, vectors: List[str]) -> str:
        """Identify attack vectors"""
        return f"""{requirement} opens these attack vectors:
        {chr(10).join(f'- {vector}' for vector in vectors)}
        Each vector requires additional security controls.
        We're increasing our attack surface by 40%."""
    
    def _compliance_nightmare(self, requirement: str, regulations: List[str]) -> str:
        """Highlight compliance issues"""
        return f"""{requirement} violates these regulations:
        {chr(10).join(f'- {reg}' for reg in regulations)}
        Compliance cost: $2M+ in audits and remediation.
        Legal risk: Unbounded."""
    
    def _breach_scenario(self, requirement: str) -> str:
        """Paint a breach scenario"""
        return f"""Here's how {requirement} gets us breached:
        1. Attacker finds the new API endpoint
        2. Exploits the race condition we didn't consider
        3. Exfiltrates user data
        4. We're on the front page of HackerNews
        5. Stock price drops 30%
        This isn't hypothetical - I've seen this exact pattern 3 times."""


def create_con_team(llm_config: Optional[Dict] = None) -> List[Agent]:
    """Create the complete CON team of agents"""
    
    # Initialize agents with optional LLM configuration
    senior_architect = SeniorArchitectAgent()
    qa_engineer = QAEngineerAgent()
    data_analyst = DataAnalystAgent()
    security_expert = SecurityExpertAgent()
    
    # Import tools
    from ..research.searcher import create_research_tools
    tools = create_research_tools()
    
    # Create and return the team
    return [
        senior_architect.create_agent(tools),
        qa_engineer.create_agent(tools),
        data_analyst.create_agent(tools),
        security_expert.create_agent(tools)
    ]


def get_con_team_metadata() -> Dict:
    """Get metadata about the CON team for UI display"""
    return {
        "team_name": "Requirement Skeptics",
        "team_color": "#EF4444",  # Red
        "team_emoji": "❤️",
        "members": [
            {
                "name": "Senior Architect",
                "emoji": "🏗️",
                "strength": "Technical Reality",
                "quote": "I've seen this movie before. It doesn't end well."
            },
            {
                "name": "QA Engineer",
                "emoji": "🔍",
                "strength": "Edge Cases & Failures",
                "quote": "Users will break this in ways you can't imagine"
            },
            {
                "name": "Data Analyst",
                "emoji": "📊",
                "strength": "ROI & Usage Reality",
                "quote": "Numbers don't lie, but wishful thinking does"
            },
            {
                "name": "Security Expert",
                "emoji": "🔒",
                "strength": "Security & Compliance",
                "quote": "Every feature is a potential breach"
            }
        ]
    }
#built with love
