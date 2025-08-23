#!/usr/bin/env python3
"""
Real ReqDefender Streamlit interface integrated with actual debate system
"""

import streamlit as st
import asyncio
import sys
import os
from pathlib import Path
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import our actual ReqDefender modules
try:
    from research.searcher_working import WorkingResearchPipeline
    # Import evidence system directly to avoid arena __init__ dependencies
    sys.path.append(os.path.join(project_root, 'arena'))
    from evidence_system import EvidenceGatherer, EvidenceScorer, EvidenceValidator
    
    # Import LLM clients
    import openai
    from anthropic import Anthropic
    
    MODULES_AVAILABLE = True
    LLM_AVAILABLE = True
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Some modules require additional dependencies. Running in limited mode.")
    MODULES_AVAILABLE = False
    LLM_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="ReqDefender - Real Debate Arena",
    page_icon="🛡️",
    layout="wide"
)

# Enhanced CSS with fixed evidence cards
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #F1F5F9;
    }
    
    .big-title {
        font-size: 3rem;
        text-align: center;
        color: #60A5FA;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #94A3B8;
        margin-bottom: 2rem;
    }
    
    .verdict-approved {
        background: linear-gradient(135deg, #065F46 0%, #047857 100%);
        border: 2px solid #10B981;
        padding: 1.5rem;
        border-radius: 0.75rem;
        color: #D1FAE5;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    .verdict-rejected {
        background: linear-gradient(135deg, #991B1B 0%, #DC2626 100%);
        border: 2px solid #EF4444;
        padding: 1.5rem;
        border-radius: 0.75rem;
        color: #FEE2E2;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }
    
    .verdict-research {
        background: linear-gradient(135deg, #92400E 0%, #D97706 100%);
        border: 2px solid #F59E0B;
        padding: 1.5rem;
        border-radius: 0.75rem;
        color: #FEF3C7;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }
    
    .evidence-analysis {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 2px solid #8B5CF6;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #E2E8F0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.2);
    }
    
    .evidence-card {
        background: linear-gradient(135deg, #1F2937 0%, #111827 100%) !important;
        border: 2px solid #3B82F6 !important;
        color: #F3F4F6 !important;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .evidence-card strong {
        color: #60A5FA !important;
    }
    
    .evidence-card em {
        color: #F3F4F6 !important;
    }
    
    .evidence-card small {
        color: #D1D5DB !important;
    }
    
    .agent-card {
        background: linear-gradient(135deg, #1F2937 0%, #111827 100%);
        color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        margin: 0.75rem 0;
    }
    
    .pro-team {
        border-left: 4px solid #10B981;
    }
    
    .con-team {
        border-left: 4px solid #EF4444;
    }
    
    .phase-indicator {
        background: linear-gradient(135deg, #1E40AF 0%, #3730A3 100%);
        color: #F1F5F9;
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

class ReqDefenderApp:
    """Main application class for real ReqDefender interface"""
    
    def __init__(self):
        self.initialize_session_state()
        
        # Initialize components if modules are available
        if MODULES_AVAILABLE:
            self.research_pipeline = WorkingResearchPipeline()
            self.evidence_gatherer = EvidenceGatherer()
            self.evidence_scorer = EvidenceScorer()
            self.evidence_validator = EvidenceValidator()
        else:
            self.research_pipeline = None
            self.evidence_gatherer = None
            self.evidence_scorer = None
            self.evidence_validator = None
        
        # Initialize LLM clients
        if LLM_AVAILABLE:
            self.setup_llm_clients()
        else:
            self.openai_client = None
            self.anthropic_client = None
    
    def setup_llm_clients(self):
        """Initialize LLM API clients"""
        from config import ReqDefenderConfig
        server_config = ReqDefenderConfig.get_server_config()
        
        if server_config.get('debug'):
            st.sidebar.info("🔧 Debug mode enabled")
        
        if server_config.get('disable_cache') or server_config.get('force_fresh_responses'):
            st.sidebar.info("🔄 Cache disabled - fresh responses only")
        
        try:
            # Try Anthropic first (if available)
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key and "your_anthropic" not in anthropic_key:
                self.anthropic_client = Anthropic(api_key=anthropic_key)
                st.sidebar.success("🤖 Anthropic Claude: Ready")
            else:
                self.anthropic_client = None
            
            # Try OpenAI as backup
            openai_key = os.getenv("OPENAI_API_KEY") 
            if openai_key and "your_openai" not in openai_key:
                self.openai_client = openai.OpenAI(api_key=openai_key)
                st.sidebar.success("🤖 OpenAI GPT: Ready")
            else:
                self.openai_client = None
            
            if not self.anthropic_client and not self.openai_client:
                st.sidebar.warning("⚠️ No LLM API keys found - using mock agents")
                
        except Exception as e:
            st.sidebar.error(f"❌ LLM setup failed: {e}")
            self.anthropic_client = None
            self.openai_client = None
    
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if "debate_active" not in st.session_state:
            st.session_state.debate_active = False
        if "debate_phase" not in st.session_state:
            st.session_state.debate_phase = None
        if "evidence_collected" not in st.session_state:
            st.session_state.evidence_collected = []
        if "debate_history" not in st.session_state:
            st.session_state.debate_history = []
        if "current_requirement" not in st.session_state:
            st.session_state.current_requirement = ""
        if "pro_arguments" not in st.session_state:
            st.session_state.pro_arguments = []
        if "con_arguments" not in st.session_state:
            st.session_state.con_arguments = []
        if "final_verdict" not in st.session_state:
            st.session_state.final_verdict = None
    
    def render_header(self):
        """Render the application header"""
        st.markdown('<h1 class="big-title">🛡️ ReqDefender</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Real AI Agent Debate System - Powered by Evidence & Logic</p>', unsafe_allow_html=True)
        
        # Show system status
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔍 Search System", "DuckDuckGo Ready" if self.research_pipeline else "Offline")
        with col2:
            st.metric("📊 Evidence System", "Operational" if self.evidence_gatherer else "Offline") 
        with col3:
            st.metric("🎭 Agent System", "Mock Mode")  # TODO: Change when real agents integrated
        
        st.markdown("---")
    
    def render_sidebar(self):
        """Render configuration sidebar"""
        with st.sidebar:
            st.header("⚙️ Real Configuration")
            
            # Judge selection
            judge_type = st.selectbox(
                "Judge Personality",
                ["Pragmatist", "Innovator", "User Advocate"],
                help="AI judge personality affects decision weighting"
            )
            
            # Debate intensity affects evidence gathering depth
            intensity = st.select_slider(
                "Analysis Depth",
                options=["Quick", "Standard", "Deep"],
                value="Standard",
                help="Affects evidence gathering and analysis depth"
            )
            
            # Evidence settings
            st.subheader("📊 Evidence Settings")
            max_evidence = st.slider("Max Evidence Sources", 3, 20, 10)
            evidence_threshold = st.slider("Evidence Quality Threshold", 0.0, 1.0, 0.3)
            
            # Search settings  
            st.subheader("🔍 Search Settings")
            search_timeout = st.slider("Search Timeout (seconds)", 5, 30, 15)
            
            st.markdown("---")
            
            # Real agent information
            st.subheader("🎭 Agent Teams")
            st.markdown("""
            **PRO Team 💚**
            - Product Visionary
            - Sales Champion  
            - UX Designer
            
            **CON Team ❤️**
            - Senior Architect
            - QA Engineer
            - Data Analyst
            
            **Judge ⚖️**
            - Selected: {judge}
            """.format(judge=judge_type))
            
            return {
                "judge_type": judge_type,
                "intensity": intensity,
                "max_evidence": max_evidence,
                "evidence_threshold": evidence_threshold,
                "search_timeout": search_timeout
            }
    
    def render_requirement_input(self):
        """Render requirement input section"""
        st.markdown("### 📝 Enter Your Requirement for Analysis")
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            requirement = st.text_area(
                "What feature or requirement needs debate?",
                placeholder="e.g., 'Implement blockchain-based user authentication', 'Add real-time collaboration features'",
                height=100,
                key="requirement_input"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            analyze_button = st.button(
                "🚀 Start Real Debate",
                type="primary",
                use_container_width=True,
                disabled=st.session_state.debate_active
            )
        
        # Example requirements
        st.markdown("**Professional Examples:**")
        examples = [
            "Implement OAuth 2.0 authentication system",
            "Migrate from monolith to microservices architecture", 
            "Add GraphQL API layer to replace REST endpoints",
            "Deploy application using Kubernetes orchestration"
        ]
        
        cols = st.columns(len(examples))
        for i, example in enumerate(examples):
            with cols[i]:
                if st.button(f"💡 {example[:20]}...", key=f"example_{i}"):
                    st.session_state.requirement_input = example
                    st.rerun()
        
        return requirement, analyze_button
    
    async def gather_real_evidence(self, requirement: str, config: dict):
        """Gather real evidence using our evidence system"""
        st.session_state.debate_phase = "🔍 Evidence Gathering"
        
        evidence_container = st.container()
        with evidence_container:
            st.markdown('<div class="phase-indicator"><h3>🔍 Gathering Evidence from Multiple Sources</h3></div>', 
                       unsafe_allow_html=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Search for evidence
                status_text.info("🔍 Searching for evidence...")
                progress_bar.progress(0.2)
                
                pro_evidence = await self.research_pipeline.search_evidence(requirement, "support")
                await asyncio.sleep(1)  # Small delay for UX
                
                progress_bar.progress(0.4)
                status_text.info("🔍 Searching for counter-evidence...")
                
                con_evidence = await self.research_pipeline.search_evidence(requirement, "oppose") 
                await asyncio.sleep(1)
                
                progress_bar.progress(0.6)
                status_text.info("📊 Processing and scoring evidence...")
                
                # Step 2: Process evidence (use existing results, don't search again!)
                all_evidence = []
                
                # Convert search results to evidence format
                for evidence_data in pro_evidence[:3]:  # Limit PRO evidence
                    evidence_obj = {
                        'content': evidence_data.get('snippet', 'Supporting evidence found'),
                        'source': evidence_data.get('source', 'Web Search'),
                        'url': evidence_data.get('url', ''),
                        'tier': 'SILVER',  # Default tier
                        'stance': 'PRO',
                        'confidence': 0.7
                    }
                    all_evidence.append(evidence_obj)
                
                progress_bar.progress(0.8)
                
                # Convert CON evidence  
                for evidence_data in con_evidence[:3]:  # Limit CON evidence
                    evidence_obj = {
                        'content': evidence_data.get('snippet', 'Opposing evidence found'),
                        'source': evidence_data.get('source', 'Web Search'),
                        'url': evidence_data.get('url', ''),
                        'tier': 'SILVER',  # Default tier
                        'stance': 'CON',
                        'confidence': 0.7
                    }
                    all_evidence.append(evidence_obj)
                
                progress_bar.progress(1.0)
                status_text.success(f"✅ Collected {len(all_evidence)} pieces of evidence")
                
                # Store evidence
                st.session_state.evidence_collected = all_evidence
                
                # AI-powered evidence analysis
                if all_evidence and (self.anthropic_client or self.openai_client):
                    evidence_analysis = await self.analyze_evidence_quality(requirement, all_evidence)
                    st.session_state.evidence_analysis = evidence_analysis
                    
                    # Display AI analysis
                    if evidence_analysis:
                        st.markdown("### 🤖 AI Evidence Quality Analysis")
                        st.markdown(f"""
                        <div class="evidence-analysis">
                            <p><strong>Overall Quality:</strong> {evidence_analysis.get('quality_score', 'N/A')}/10</p>
                            <p><strong>Evidence Strength:</strong> {evidence_analysis.get('strength_assessment', 'Moderate')}</p>
                            <p><strong>Key Insights:</strong> {evidence_analysis.get('key_insights', 'Analysis in progress...')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Display evidence
                if all_evidence:
                    st.markdown("### 📊 Evidence Analysis Results")
                    
                    # Separate by stance
                    pro_evidence = [e for e in all_evidence if e.get('stance') == 'PRO']
                    con_evidence = [e for e in all_evidence if e.get('stance') == 'CON']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 💚 Supporting Evidence")
                        for evidence in pro_evidence[:3]:
                            self.render_evidence_card(evidence, "PRO")
                    
                    with col2:
                        st.markdown("#### ❤️ Counter Evidence")  
                        for evidence in con_evidence[:3]:
                            self.render_evidence_card(evidence, "CON")
                
                return all_evidence
                
            except Exception as e:
                st.error(f"❌ Evidence gathering failed: {e}")
                return []
    
    def render_evidence_card(self, evidence, team):
        """Render a real evidence card from our evidence system"""
        try:
            # Extract evidence details
            claim = getattr(evidence, 'claim', str(evidence)[:100])
            source = getattr(evidence, 'source', 'Unknown')
            tier = getattr(evidence, 'tier', None)
            score = getattr(evidence, 'total_score', 0.0)
            
            # Map tier to display
            tier_map = {
                "PLATINUM": "💎 PLATINUM",
                "GOLD": "🥇 GOLD", 
                "SILVER": "🥈 SILVER",
                "BRONZE": "🥉 BRONZE"
            }
            
            tier_display = tier_map.get(str(tier).upper() if tier else "BRONZE", "🥉 BRONZE")
            team_color = "#10B981" if team == "PRO" else "#EF4444"
            
            st.markdown(f"""
            <div class="evidence-card" style="border-left: 4px solid {team_color};">
                <strong style="color: #60A5FA;">{tier_display}</strong><br>
                <em style="color: #F3F4F6;">Claim:</em> {claim}<br>
                <small style="color: #D1D5DB;">Source: {source} | Score: {score:.2f}</small>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.markdown(f"""
            <div class="evidence-card">
                <strong style="color: #60A5FA;">🥉 EVIDENCE</strong><br>
                <em style="color: #F3F4F6;">Claim:</em> {str(evidence)[:100]}...<br>
                <small style="color: #D1D5DB;">Source: Research | Error: {str(e)}</small>
            </div>
            """, unsafe_allow_html=True)
    
    async def simulate_agent_debate(self, requirement: str, evidence: list, config: dict):
        """Simulate agent debate using collected evidence"""
        st.session_state.debate_phase = "⚔️ Agent Debate"
        
        st.markdown('<div class="phase-indicator"><h3>⚔️ AI Agents Analyzing Evidence</h3></div>', 
                   unsafe_allow_html=True)
        
        # Generate arguments based on real evidence
        pro_args = await self.generate_pro_arguments(requirement, evidence)
        con_args = await self.generate_con_arguments(requirement, evidence)
        
        # Display debate
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💚 PRO Team Arguments")
            for i, arg in enumerate(pro_args, 1):
                st.markdown(f"""
                <div class="agent-card pro-team">
                    <strong style="color: #10B981;">Agent {i}:</strong><br>
                    {arg}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### ❤️ CON Team Arguments")
            for i, arg in enumerate(con_args, 1):
                st.markdown(f"""
                <div class="agent-card con-team">
                    <strong style="color: #EF4444;">Agent {i}:</strong><br>
                    {arg}
                </div>
                """, unsafe_allow_html=True)
        
        # Store arguments
        st.session_state.pro_arguments = pro_args
        st.session_state.con_arguments = con_args
        
        return pro_args, con_args
    
    async def generate_pro_arguments(self, requirement: str, evidence: list) -> list:
        """Generate PRO arguments using real AI agents"""
        import time
        start_time = time.time()
        
        st.write(f"🔍 DEBUG: Starting PRO argument generation...")
        st.write(f"🔍 DEBUG: Anthropic client available: {self.anthropic_client is not None}")
        st.write(f"🔍 DEBUG: OpenAI client available: {self.openai_client is not None}")
        
        if not self.anthropic_client and not self.openai_client:
            # Fallback to template if no LLM available
            return [
                f"The evidence supports implementing {requirement} based on {len(evidence)} sources.",
                f"This requirement addresses documented user needs and industry trends.",
                f"Technical feasibility is demonstrated by similar implementations."
            ]
        
        # Prepare evidence summary for LLM
        evidence_summary = "\n".join([
            f"- {str(e)[:200]}..." if len(str(e)) > 200 else f"- {str(e)}"
            for e in evidence[:5]  # Limit to 5 pieces for token efficiency
        ])
        
        prompt = f"""You are a PRO team agent in a requirements debate. Your job is to argue FOR implementing this requirement.

REQUIREMENT: {requirement}

EVIDENCE AVAILABLE:
{evidence_summary}

Generate 3 strong, specific arguments supporting this requirement. Each argument should:
- Reference the evidence provided
- Be concise but compelling  
- Address practical benefits
- Sound professional and technical

Format as a simple list, one argument per line."""

        try:
            if self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                arguments_text = response.content[0].text
            else:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                arguments_text = response.choices[0].message.content
            
            # Parse arguments from response
            arguments = [arg.strip().lstrip('-').strip() 
                        for arg in arguments_text.split('\n') 
                        if arg.strip() and not arg.strip().startswith('#')][:3]
            
            end_time = time.time()
            st.write(f"🔍 DEBUG: PRO generation took {end_time - start_time:.2f}s")
            st.write(f"🔍 DEBUG: PRO arguments parsed: {len(arguments)} items")
            
            return arguments if arguments else [
                "Based on the evidence, this requirement shows strong potential for success.",
                "The research indicates significant user demand and technical feasibility.",
                "Implementation risks are outweighed by the documented benefits."
            ]
            
        except Exception as e:
            end_time = time.time()
            st.error(f"❌ PRO argument generation failed: {e}")
            st.write(f"🔍 DEBUG: PRO generation failed after {end_time - start_time:.2f}s")
            return [
                f"Evidence supports {requirement} with {len(evidence)} sources backing implementation.",
                "Research indicates this addresses a real market need with proven solutions.",
                "Technical analysis shows feasible implementation path with manageable complexity."
            ]
    
    async def generate_con_arguments(self, requirement: str, evidence: list) -> list:
        """Generate CON arguments using real AI agents"""
        import time
        start_time = time.time()
        
        st.write(f"🔍 DEBUG: Starting CON argument generation...")
        st.write(f"🔍 DEBUG: Anthropic client available: {self.anthropic_client is not None}")
        st.write(f"🔍 DEBUG: OpenAI client available: {self.openai_client is not None}")
        
        if not self.anthropic_client and not self.openai_client:
            # Fallback to template if no LLM available
            return [
                f"Implementation of {requirement} presents significant complexity risks.",
                f"Evidence shows potential issues with {len(evidence)} sources indicating concerns.",
                f"Alternative solutions may provide better ROI with lower overhead."
            ]
        
        # Prepare evidence summary for LLM
        evidence_summary = "\n".join([
            f"- {str(e)[:200]}..." if len(str(e)) > 200 else f"- {str(e)}"
            for e in evidence[:5]  # Limit to 5 pieces for token efficiency
        ])
        
        prompt = f"""You are a CON team agent in a requirements debate. Your job is to argue AGAINST implementing this requirement.

REQUIREMENT: {requirement}

EVIDENCE AVAILABLE:
{evidence_summary}

Generate 3 strong, specific arguments opposing this requirement. Each argument should:
- Reference potential risks and issues
- Be concise but compelling
- Address practical concerns (cost, complexity, maintenance)
- Sound professional and technical

Format as a simple list, one argument per line."""

        try:
            if self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                arguments_text = response.content[0].text
            else:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                arguments_text = response.choices[0].message.content
            
            # Parse arguments from response
            arguments = [arg.strip().lstrip('-').strip() 
                        for arg in arguments_text.split('\n') 
                        if arg.strip() and not arg.strip().startswith('#')][:3]
            
            end_time = time.time()
            st.write(f"🔍 DEBUG: CON generation took {end_time - start_time:.2f}s")
            st.write(f"🔍 DEBUG: CON arguments parsed: {len(arguments)} items")
            
            return arguments if arguments else [
                "Implementation complexity exceeds potential benefits based on available evidence.",
                "Resource allocation concerns outweigh the documented advantages.",
                "Alternative approaches may deliver similar value with reduced risk."
            ]
            
        except Exception as e:
            end_time = time.time()
            st.error(f"❌ CON argument generation failed: {e}")
            st.write(f"🔍 DEBUG: CON generation failed after {end_time - start_time:.2f}s")
            return [
                f"The {requirement} implementation presents significant technical and resource risks.",
                "Evidence indicates potential maintenance burden and complexity concerns.",
                "Alternative solutions may achieve similar goals with lower implementation costs."
            ]
    
    async def generate_final_judgment(self, requirement: str, pro_args: list, con_args: list, evidence: list, config: dict):
        """Generate final judgment based on debate using AI judge"""
        st.session_state.debate_phase = "⚖️ Final Judgment"
        
        st.markdown('<div class="phase-indicator"><h3>⚖️ AI Judge Analyzing Arguments & Evidence</h3></div>', 
                   unsafe_allow_html=True)
        
        # Show deliberation process
        with st.spinner("AI Judge analyzing evidence and arguments..."):
            time.sleep(2)  # Brief pause for UX
            
            if not self.anthropic_client and not self.openai_client:
                # Fallback to simple scoring if no LLM available
                return self._generate_fallback_judgment(requirement, pro_args, con_args, evidence, config)
            
            # Prepare comprehensive prompt for AI judge
            pro_summary = "\n".join([f"- {arg}" for arg in pro_args])
            con_summary = "\n".join([f"- {arg}" for arg in con_args])
            evidence_summary = "\n".join([
                f"- {str(e)[:150]}..." if len(str(e)) > 150 else f"- {str(e)}"
                for e in evidence[:8]  # Limit to 8 pieces for token efficiency
            ])
            
            judge_personality = {
                "Pragmatist": "You prioritize practical implementation concerns, cost-benefit analysis, and proven solutions. You're skeptical of unproven approaches.",
                "Innovator": "You favor cutting-edge solutions, creative approaches, and calculated risks for competitive advantage. You're optimistic about new technologies.",
                "User Advocate": "You prioritize user experience, accessibility, and features that directly benefit end users. You're cautious about complexity that doesn't serve users."
            }
            
            personality_context = judge_personality.get(config["judge_type"], judge_personality["Pragmatist"])
            
            prompt = f"""You are an experienced software engineering judge with the personality of a {config['judge_type']}. {personality_context}

REQUIREMENT TO EVALUATE: {requirement}

PRO TEAM ARGUMENTS:
{pro_summary}

CON TEAM ARGUMENTS:
{con_summary}

RESEARCH EVIDENCE:
{evidence_summary}

Your task is to make a final verdict on whether this requirement should be implemented. Consider:
1. Technical feasibility and complexity
2. Business value and user benefit
3. Resource requirements and timeline
4. Risk factors and potential issues
5. Evidence quality and relevance
6. Argument strength and logic

Provide your verdict as one of: APPROVED, REJECTED, or NEEDS_RESEARCH

Format your response as:
VERDICT: [APPROVED/REJECTED/NEEDS_RESEARCH]
CONFIDENCE: [0-100]%
REASONING: [2-3 sentences explaining your decision, referencing specific evidence and arguments]
KEY_FACTORS: [Main factors that influenced your decision]"""

            try:
                if self.anthropic_client:
                    response = self.anthropic_client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=800,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    judgment_text = response.content[0].text
                else:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        max_tokens=800,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    judgment_text = response.choices[0].message.content
                
                # Parse AI response
                judgment = self._parse_ai_judgment(judgment_text, requirement, pro_args, con_args, evidence, config)
                
            except Exception as e:
                st.error(f"❌ AI Judge failed: {e}")
                judgment = self._generate_fallback_judgment(requirement, pro_args, con_args, evidence, config)
            
            st.session_state.final_verdict = judgment
            return judgment
    
    def _parse_ai_judgment(self, judgment_text: str, requirement: str, pro_args: list, con_args: list, evidence: list, config: dict) -> dict:
        """Parse AI judge response into structured judgment"""
        lines = judgment_text.strip().split('\n')
        verdict = "NEEDS_RESEARCH"
        confidence = 75.0
        reasoning = f"AI analysis of {requirement} based on available evidence and arguments."
        key_factors = "Technical complexity, business value, implementation risk"
        
        for line in lines:
            line = line.strip()
            if line.startswith("VERDICT:"):
                verdict_text = line.replace("VERDICT:", "").strip()
                if "APPROVED" in verdict_text.upper():
                    verdict = "APPROVED"
                elif "REJECTED" in verdict_text.upper():
                    verdict = "REJECTED"
                elif "NEEDS_RESEARCH" in verdict_text.upper():
                    verdict = "NEEDS_RESEARCH"
            elif line.startswith("CONFIDENCE:"):
                try:
                    conf_text = line.replace("CONFIDENCE:", "").strip().replace("%", "")
                    confidence = float(conf_text)
                except:
                    confidence = 75.0
            elif line.startswith("REASONING:"):
                reasoning = line.replace("REASONING:", "").strip()
            elif line.startswith("KEY_FACTORS:"):
                key_factors = line.replace("KEY_FACTORS:", "").strip()
        
        # Calculate scores for display metrics (similar to fallback method)
        pro_score = len([e for e in evidence if e.get('stance') == 'PRO']) * 10
        con_score = len([e for e in evidence if e.get('stance') == 'CON']) * 10
        pro_score += len(pro_args) * 5
        con_score += len(con_args) * 5
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning,
            "key_factors": key_factors,
            "evidence_count": len(evidence),
            "pro_score": pro_score,
            "con_score": con_score,
            "judge_type": config["judge_type"],
            "ai_powered": True
        }
    
    def _generate_fallback_judgment(self, requirement: str, pro_args: list, con_args: list, evidence: list, config: dict) -> dict:
        """Generate fallback judgment when AI is not available"""
        # Calculate verdict based on evidence quality and quantity
        pro_score = len([e for e in evidence if e.get('stance') == 'PRO']) * 10
        con_score = len([e for e in evidence if e.get('stance') == 'CON']) * 10
        
        # Add argument strength (simplified)
        pro_score += len(pro_args) * 5
        con_score += len(con_args) * 5
        
        # Judge bias factor
        judge_bias = {
            "Pragmatist": 0.0,    # Neutral
            "Innovator": 0.2,     # Slightly pro-innovation
            "User Advocate": -0.1  # Slightly conservative
        }
        
        bias = judge_bias.get(config["judge_type"], 0.0)
        pro_score += pro_score * bias
        
        # Generate verdict
        if pro_score > con_score * 1.2:
            verdict = "APPROVED"
            confidence = min(95, 60 + (pro_score - con_score))
        elif con_score > pro_score * 1.2:
            verdict = "REJECTED" 
            confidence = min(95, 60 + (con_score - pro_score))
        else:
            verdict = "NEEDS_RESEARCH"
            confidence = 50 + abs(pro_score - con_score) * 0.1
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": f"Based on analysis of {len(evidence)} evidence sources and agent arguments, "
                       f"the {config['judge_type']} judge has determined this requirement should be {verdict.lower()}.",
            "evidence_count": len(evidence),
            "pro_score": pro_score,
            "con_score": con_score,
            "judge_type": config["judge_type"],
            "ai_powered": False
        }
    
    async def analyze_evidence_quality(self, requirement: str, evidence: list) -> dict:
        """Analyze evidence quality using AI"""
        if not self.anthropic_client and not self.openai_client:
            return {}
        
        # Prepare evidence summary for analysis
        evidence_summary = "\n".join([
            f"Evidence {i+1}: {str(e)[:200]}..." if len(str(e)) > 200 else f"Evidence {i+1}: {str(e)}"
            for i, e in enumerate(evidence[:8])  # Analyze up to 8 pieces
        ])
        
        prompt = f"""You are an expert research analyst evaluating evidence quality for software engineering decisions.

REQUIREMENT: {requirement}

EVIDENCE TO ANALYZE:
{evidence_summary}

Evaluate the overall evidence quality and provide:
1. Quality Score (0-10): Rate the overall quality of evidence
2. Strength Assessment: Strong/Moderate/Weak  
3. Key Insights: 2-3 sentences about what the evidence reveals

Consider factors like:
- Credibility and source reliability
- Relevance to the specific requirement
- Recency and timeliness
- Depth and specificity
- Balance of perspectives
- Technical accuracy

Format your response as:
QUALITY_SCORE: [0-10]
STRENGTH_ASSESSMENT: [Strong/Moderate/Weak]
KEY_INSIGHTS: [Your analysis in 2-3 sentences]"""

        try:
            if self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=400,
                    messages=[{"role": "user", "content": prompt}]
                )
                analysis_text = response.content[0].text
            else:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    max_tokens=400,
                    messages=[{"role": "user", "content": prompt}]
                )
                analysis_text = response.choices[0].message.content
            
            # Parse analysis response
            return self._parse_evidence_analysis(analysis_text)
            
        except Exception as e:
            st.error(f"❌ Evidence analysis failed: {e}")
            return {}
    
    def _parse_evidence_analysis(self, analysis_text: str) -> dict:
        """Parse AI evidence analysis response"""
        lines = analysis_text.strip().split('\n')
        quality_score = "N/A"
        strength_assessment = "Moderate"
        key_insights = "Evidence analysis completed."
        
        for line in lines:
            line = line.strip()
            if line.startswith("QUALITY_SCORE:"):
                quality_score = line.replace("QUALITY_SCORE:", "").strip()
            elif line.startswith("STRENGTH_ASSESSMENT:"):
                strength_assessment = line.replace("STRENGTH_ASSESSMENT:", "").strip()
            elif line.startswith("KEY_INSIGHTS:"):
                key_insights = line.replace("KEY_INSIGHTS:", "").strip()
        
        return {
            "quality_score": quality_score,
            "strength_assessment": strength_assessment,
            "key_insights": key_insights
        }
    
    def render_final_verdict(self, verdict: dict):
        """Render the final verdict"""
        st.markdown("---")
        st.markdown("## 🏛️ Final Judgment")
        
        # Show AI-powered indicator if applicable
        ai_indicator = "🤖 AI-Powered" if verdict.get("ai_powered", False) else "📊 Rule-Based"
        
        if verdict["verdict"] == "APPROVED":
            st.markdown(f"""
            <div class="verdict-approved">
                <h2 style="text-align: center;">✅ VERDICT: APPROVED ✅</h2>
                <h3 style="text-align: center;">Judge Confidence: {verdict['confidence']:.1f}%</h3>
                <p><strong>{ai_indicator} Judge ({verdict['judge_type']}):</strong> {verdict['reasoning']}</p>
                <p><strong>Evidence Analysis:</strong> {verdict['evidence_count']} sources reviewed</p>
                {f"<p><strong>Key Factors:</strong> {verdict['key_factors']}</p>" if verdict.get('key_factors') else ""}
                {f"<p><strong>Score:</strong> PRO {verdict.get('pro_score', 0):.1f} vs CON {verdict.get('con_score', 0):.1f}</p>" if verdict.get('pro_score') is not None else ""}
            </div>
            """, unsafe_allow_html=True)
            st.balloons()
            
        elif verdict["verdict"] == "REJECTED":
            st.markdown(f"""
            <div class="verdict-rejected">
                <h2 style="text-align: center;">❌ VERDICT: REJECTED ❌</h2>
                <h3 style="text-align: center;">Judge Confidence: {verdict['confidence']:.1f}%</h3>
                <p><strong>{ai_indicator} Judge ({verdict['judge_type']}):</strong> {verdict['reasoning']}</p>
                <p><strong>Evidence Analysis:</strong> {verdict['evidence_count']} sources reviewed</p>
                {f"<p><strong>Key Factors:</strong> {verdict['key_factors']}</p>" if verdict.get('key_factors') else ""}
                {f"<p><strong>Score:</strong> PRO {verdict.get('pro_score', 0):.1f} vs CON {verdict.get('con_score', 0):.1f}</p>" if verdict.get('pro_score') is not None else ""}
            </div>
            """, unsafe_allow_html=True)
            
        else:  # NEEDS_RESEARCH
            st.markdown(f"""
            <div class="verdict-research">
                <h2 style="text-align: center;">🔍 VERDICT: NEEDS MORE RESEARCH 🔍</h2>
                <h3 style="text-align: center;">Judge Confidence: {verdict['confidence']:.1f}%</h3>
                <p><strong>{ai_indicator} Judge ({verdict['judge_type']}):</strong> {verdict['reasoning']}</p>
                <p><strong>Evidence Analysis:</strong> {verdict['evidence_count']} sources reviewed</p>
                {f"<p><strong>Key Factors:</strong> {verdict['key_factors']}</p>" if verdict.get('key_factors') else ""}
                {f"<p><strong>Score:</strong> PRO {verdict.get('pro_score', 0):.1f} vs CON {verdict.get('con_score', 0):.1f}</p>" if verdict.get('pro_score') is not None else ""}
            </div>
            """, unsafe_allow_html=True)
    
    def run_real_debate(self, requirement: str, config: dict):
        """Run the complete real debate process"""
        st.session_state.debate_active = True
        st.session_state.current_requirement = requirement
        
        # Add cache busting for fresh responses
        from config import ReqDefenderConfig
        server_config = ReqDefenderConfig.get_server_config()
        
        if server_config.get('disable_cache') or server_config.get('force_fresh_responses'):
            st.info("🔄 Cache disabled - forcing fresh responses")
            # Clear any cached session state
            cache_keys = ['final_verdict', 'pro_arguments', 'con_arguments', 'evidence_results']
            for key in cache_keys:
                if key in st.session_state:
                    del st.session_state[key]
        
        try:
            # Helper function to run async code safely
            def run_async(coro):
                import asyncio
                try:
                    # Try to get existing event loop
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If loop is running, use thread pool
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, coro)
                            return future.result()
                    else:
                        return asyncio.run(coro)
                except RuntimeError:
                    # No event loop, create new one
                    return asyncio.run(coro)
            
            # Step 1: Gather Evidence
            st.write("🔍 DEBUG: Starting evidence gathering...")
            evidence = run_async(self.gather_real_evidence(requirement, config))
            st.write(f"🔍 DEBUG: Evidence gathered: {len(evidence)} pieces")
            
            # Step 2: Agent Debate  
            if evidence:
                try:
                    st.write("🔍 DEBUG: Starting agent debate...")
                    pro_args, con_args = run_async(self.simulate_agent_debate(requirement, evidence, config))
                    st.write(f"🔍 DEBUG: Arguments generated - PRO: {len(pro_args)}, CON: {len(con_args)}")
                    
                    # Step 3: Final Judgment
                    st.write("🔍 DEBUG: Starting final judgment...")
                    verdict = run_async(self.generate_final_judgment(requirement, pro_args, con_args, evidence, config))
                    st.write(f"🔍 DEBUG: Judgment complete: {verdict.get('verdict', 'Unknown')}")
                except Exception as e:
                    st.error(f"❌ Agent debate failed: {e}")
                    # Generate verdict with empty arguments as fallback
                    pro_args, con_args = [], []
                    verdict = run_async(self.generate_final_judgment(requirement, pro_args, con_args, evidence, config))
                
                # Step 4: Display Results
                self.render_final_verdict(verdict)
            else:
                st.error("❌ Could not gather sufficient evidence for debate")
                
        except Exception as e:
            st.error(f"❌ Debate process failed: {e}")
            import traceback
            st.error(f"Debug info: {traceback.format_exc()}")
        finally:
            st.session_state.debate_active = False
    
    def run(self):
        """Main application entry point"""
        self.render_header()
        
        # Sidebar configuration
        config = self.render_sidebar()
        
        # Main content area
        requirement, analyze_button = self.render_requirement_input()
        
        st.divider()
        
        # Start real debate if button clicked
        if analyze_button and requirement:
            # Clear previous results BEFORE starting new analysis
            st.session_state.final_verdict = None
            st.session_state.pro_arguments = []
            st.session_state.con_arguments = []
            st.session_state.evidence_collected = []
            st.session_state.debate_phase = None
            
            self.run_real_debate(requirement, config)
        
        # Show current status
        if st.session_state.debate_active:
            st.info(f"🎭 Current Phase: {st.session_state.debate_phase}")
        
        # Show results if available (only after debate completes)
        if st.session_state.final_verdict and not st.session_state.debate_active:
            st.markdown("### 📊 Debate Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Evidence Sources", st.session_state.final_verdict["evidence_count"])
            with col2:
                st.metric("PRO Score", f"{st.session_state.final_verdict['pro_score']:.1f}")
            with col3:
                st.metric("CON Score", f"{st.session_state.final_verdict['con_score']:.1f}")


def main():
    """Application entry point"""
    app = ReqDefenderApp()
    app.run()


if __name__ == "__main__":
    main()
#built with love
