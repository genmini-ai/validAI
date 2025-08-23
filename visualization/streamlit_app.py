# visualization/streamlit_app.py
"""Streamlit web interface for ReqDefender's Agent Debate Arena"""

import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass
import time

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from arena.debate_orchestrator import DebateOrchestrator, DebatePhase
from agents.pro_team_agents import create_pro_team, get_pro_team_metadata
from agents.con_team_agents import create_con_team, get_con_team_metadata
from agents.judge_agent import create_judge, get_judge_metadata


# Page configuration
st.set_page_config(
    page_title="ReqDefender - Agent Debate Arena",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for theatrical effects
st.markdown("""
<style>
    /* Dark theme for better contrast */
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #F1F5F9;
    }
    
    .debate-arena {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin: 1rem 0;
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    .evidence-section-header {
        background: linear-gradient(135deg, #1E40AF 0%, #3730A3 100%);
        color: #F1F5F9;
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        margin: 1.5rem 0 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        border: 2px solid rgba(59, 130, 246, 0.3);
    }
    
    .agent-card {
        background: linear-gradient(135deg, #1F2937 0%, #111827 100%);
        color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        margin: 0.75rem 0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .agent-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4);
    }
    
    .pro-team {
        border-left: 4px solid #10B981;
    }
    
    .con-team {
        border-left: 4px solid #EF4444;
    }
    
    .evidence-tier-1, .evidence-tier-1 *, .evidence-tier-1 div, .evidence-tier-1 span, .evidence-tier-1 p, .evidence-tier-1 strong, .evidence-tier-1 small {
        background: linear-gradient(135deg, #2D1B69 0%, #1F1347 100%) !important;
        border: 2px solid #FFD700 !important;
        color: #FFD700 !important;
    }
    
    .evidence-tier-2, .evidence-tier-2 *, .evidence-tier-2 div, .evidence-tier-2 span, .evidence-tier-2 p, .evidence-tier-2 strong, .evidence-tier-2 small {
        background: linear-gradient(135deg, #4C1D95 0%, #2D1B69 100%) !important;
        border: 2px solid #C0C0C0 !important;
        color: #E5E7EB !important;
    }
    
    .evidence-tier-3, .evidence-tier-3 *, .evidence-tier-3 div, .evidence-tier-3 span, .evidence-tier-3 p, .evidence-tier-3 strong, .evidence-tier-3 small {
        background: linear-gradient(135deg, #1F2937 0%, #111827 100%) !important;
        border: 2px solid #CD7F32 !important;
        color: #D1D5DB !important;
    }
    
    .evidence-tier-4, .evidence-tier-4 *, .evidence-tier-4 div, .evidence-tier-4 span, .evidence-tier-4 p, .evidence-tier-4 strong, .evidence-tier-4 small {
        background: linear-gradient(135deg, #374151 0%, #1F2937 100%) !important;
        border: 1px solid #6B7280 !important;
        color: #F3F4F6 !important;
    }
    
    /* Additional fallback styling to override Streamlit defaults */
    div[class*="evidence-tier"] {
        background: #1F2937 !important;
        color: #F3F4F6 !important;
    }
    
    div[class*="evidence-tier"] * {
        color: inherit !important;
    }
    
    /* Aggressive override for any white backgrounds in evidence sections */
    .evidence-tier-1, .evidence-tier-1 > *, .evidence-tier-1 div {
        background-color: #2D1B69 !important;
        background: linear-gradient(135deg, #2D1B69 0%, #1F1347 100%) !important;
    }
    
    .evidence-tier-2, .evidence-tier-2 > *, .evidence-tier-2 div {
        background-color: #4C1D95 !important;
        background: linear-gradient(135deg, #4C1D95 0%, #2D1B69 100%) !important;
    }
    
    .evidence-tier-3, .evidence-tier-3 > *, .evidence-tier-3 div {
        background-color: #1F2937 !important;
        background: linear-gradient(135deg, #1F2937 0%, #111827 100%) !important;
    }
    
    .evidence-tier-4, .evidence-tier-4 > *, .evidence-tier-4 div {
        background-color: #374151 !important;
        background: linear-gradient(135deg, #374151 0%, #1F2937 100%) !important;
    }
    
    .objection-splash {
        animation: shake 0.5s;
        color: #EF4444;
        font-size: 2rem;
        font-weight: bold;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    
    .dramatic-moment {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .knockout-animation {
        animation: fall 1s ease-in;
    }
    
    @keyframes fall {
        from { transform: rotate(0deg); opacity: 1; }
        to { transform: rotate(90deg); opacity: 0; }
    }
</style>
""", unsafe_allow_html=True)


class DebateUI:
    """Main UI controller for the debate arena"""
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if "debate_active" not in st.session_state:
            st.session_state.debate_active = False
        if "debate_history" not in st.session_state:
            st.session_state.debate_history = []
        if "current_phase" not in st.session_state:
            st.session_state.current_phase = None
        if "pro_confidence" not in st.session_state:
            st.session_state.pro_confidence = 50
        if "con_confidence" not in st.session_state:
            st.session_state.con_confidence = 50
        if "debate_events" not in st.session_state:
            st.session_state.debate_events = []
        if "verdict" not in st.session_state:
            st.session_state.verdict = None
    
    def render_header(self):
        """Render the application header"""
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col2:
            st.markdown("""
            <div style="text-align: center;">
                <h1>🛡️ ReqDefender</h1>
                <h3>AI Agents Debate Your Requirements to Death</h3>
                <p style="color: #666;">Watch AI agents battle over whether your feature is genius or garbage</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar controls"""
        with st.sidebar:
            st.header("⚙️ Debate Configuration")
            
            # Judge selection
            st.subheader("👨‍⚖️ Select Judge")
            judge_metadata = get_judge_metadata()
            judge_options = {j["name"]: j["type"] for j in judge_metadata["judges"]}
            selected_judge = st.selectbox(
                "Judge Personality",
                options=list(judge_options.keys()),
                help="Different judges have different biases"
            )
            
            # Show judge details
            for judge in judge_metadata["judges"]:
                if judge["name"] == selected_judge:
                    st.info(f"{judge['emoji']} **{judge['name']}**\n\n{judge['description']}\n\n*Bias: {judge['bias']}*")
            
            # Debate intensity
            st.subheader("🔥 Debate Intensity")
            intensity = st.select_slider(
                "Select intensity",
                options=["Quick", "Standard", "Deep"],
                value="Standard",
                help="Higher intensity = more evidence and longer debate"
            )
            
            # Advanced settings
            with st.expander("Advanced Settings"):
                enable_effects = st.checkbox("Enable special effects", value=True)
                max_rounds = st.number_input("Max rounds", min_value=2, max_value=6, value=4)
                evidence_threshold = st.slider("Evidence quality threshold", 0.0, 1.0, 0.5)
            
            st.divider()
            
            # Team rosters
            st.subheader("⚔️ Battle Teams")
            
            # PRO team
            pro_metadata = get_pro_team_metadata()
            st.markdown(f"### {pro_metadata['team_emoji']} {pro_metadata['team_name']}")
            for member in pro_metadata["members"]:
                st.markdown(f"{member['emoji']} **{member['name']}**  \n*{member['strength']}*")
            
            st.divider()
            
            # CON team
            con_metadata = get_con_team_metadata()
            st.markdown(f"### {con_metadata['team_emoji']} {con_metadata['team_name']}")
            for member in con_metadata["members"]:
                st.markdown(f"{member['emoji']} **{member['name']}**  \n*{member['strength']}*")
            
            return {
                "judge_type": judge_options[selected_judge],
                "intensity": intensity,
                "enable_effects": enable_effects,
                "max_rounds": max_rounds,
                "evidence_threshold": evidence_threshold
            }
    
    def render_requirement_input(self):
        """Render the requirement input section"""
        st.markdown("### 📝 Enter Your Requirement")
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            requirement = st.text_area(
                "What feature or requirement should we debate?",
                placeholder="e.g., 'Add blockchain to our todo app', 'Implement AI-powered code review', 'Build metaverse shopping experience'",
                height=100,
                key="requirement_input"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            analyze_button = st.button(
                "🎯 Start Debate",
                type="primary",
                use_container_width=True,
                disabled=st.session_state.debate_active
            )
        
        # Example requirements
        st.markdown("**Try these examples:**")
        example_cols = st.columns(3)
        
        examples = [
            "Add blockchain to our todo app",
            "Implement real-time collaboration",
            "Build AI chatbot for customer support"
        ]
        
        for i, example in enumerate(examples):
            with example_cols[i]:
                if st.button(f"💡 {example}", key=f"example_{i}"):
                    st.session_state.requirement_input = example
                    st.rerun()
        
        return requirement, analyze_button
    
    def render_confidence_meters(self):
        """Render the confidence meters"""
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pro = go.Figure(go.Indicator(
                mode="gauge+number",
                value=st.session_state.pro_confidence,
                title={"text": "💚 PRO Team Confidence"},
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#10B981"},
                    "steps": [
                        {"range": [0, 30], "color": "#FEE2E2"},
                        {"range": [30, 70], "color": "#FEF3C7"},
                        {"range": [70, 100], "color": "#D1FAE5"}
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 10
                    }
                }
            ))
            fig_pro.update_layout(height=250)
            st.plotly_chart(fig_pro, use_container_width=True)
        
        with col2:
            fig_con = go.Figure(go.Indicator(
                mode="gauge+number",
                value=st.session_state.con_confidence,
                title={"text": "❤️ CON Team Confidence"},
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#EF4444"},
                    "steps": [
                        {"range": [0, 30], "color": "#FEE2E2"},
                        {"range": [30, 70], "color": "#FEF3C7"},
                        {"range": [70, 100], "color": "#D1FAE5"}
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 10
                    }
                }
            ))
            fig_con.update_layout(height=250)
            st.plotly_chart(fig_con, use_container_width=True)
    
    def render_debate_arena(self):
        """Render the main debate arena"""
        st.markdown("""
        <div class="debate-arena">
            <h2 style="text-align: center; color: white;">⚔️ DEBATE ARENA ⚔️</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Current phase indicator
        if st.session_state.current_phase:
            phase_emoji = {
                "pre_battle": "🎭",
                "opening_statements": "📢",
                "evidence_duel": "⚔️",
                "cross_examination": "🎯",
                "final_arguments": "🏁",
                "judgment": "⚖️"
            }
            
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 0.5rem;">
                <h3>{phase_emoji.get(st.session_state.current_phase, '🎮')} Current Phase: {st.session_state.current_phase.replace('_', ' ').title()}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        # Confidence meters
        self.render_confidence_meters()
        
        # Event stream
        if st.session_state.debate_events:
            st.markdown("""
            <div class="evidence-section-header">
                <h2 style="text-align: center; margin: 0; color: inherit;">📜 Debate Transcript</h2>
            </div>
            """, unsafe_allow_html=True)
            
            event_container = st.container()
            
            # Separate evidence from other events for better organization
            evidence_events = []
            other_events = []
            
            for event in st.session_state.debate_events[-10:]:
                if event.get("event_type") == "evidence_presented":
                    evidence_events.append(event)
                else:
                    other_events.append(event)
            
            # Show evidence section if we have evidence
            if evidence_events:
                st.markdown("""
                <div class="evidence-section-header">
                    <h3 style="text-align: center; margin: 0; color: inherit;">📊 Evidence Presented</h3>
                </div>
                """, unsafe_allow_html=True)
                
                for event in evidence_events:
                    self.render_event(event)
            
            # Show other events
            with event_container:
                for event in other_events:
                    self.render_event(event)
    
    def render_event(self, event: Dict):
        """Render a single debate event"""
        event_type = event.get("event_type", "")
        
        if event_type == "agent_speaks":
            team = event["content"].get("team", "")
            agent = event.get("agent", "Unknown")
            argument = event["content"].get("argument", "")
            
            team_color = "#10B981" if team == "PRO" else "#EF4444"
            st.markdown(f"""
            <div class="agent-card {'pro-team' if team == 'PRO' else 'con-team'}">
                <strong style="color: {team_color};">{agent}</strong>
                <p>{argument}</p>
            </div>
            """, unsafe_allow_html=True)
        
        elif event_type == "evidence_presented":
            evidence = event["content"].get("evidence", {})
            tier = evidence.get("tier", 4)
            claim = evidence.get("claim", "")
            source = evidence.get("source", "")
            
            tier_names = {1: "PLATINUM", 2: "GOLD", 3: "SILVER", 4: "BRONZE"}
            tier_badge_colors = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32", 4: "#6B7280"}
            tier_badge_text = {1: "#000", 2: "#000", 3: "#FFF", 4: "#FFF"}
            tier_emojis = {1: "💎", 2: "🥇", 3: "🥈", 4: "🥉"}
            
            # Get tier-specific colors and backgrounds
            tier_configs = {
                1: {"bg": "linear-gradient(135deg, #2D1B69 0%, #1F1347 100%)", "text": "#FFD700", "border": "#FFD700"},
                2: {"bg": "linear-gradient(135deg, #4C1D95 0%, #2D1B69 100%)", "text": "#E5E7EB", "border": "#C0C0C0"},
                3: {"bg": "linear-gradient(135deg, #1F2937 0%, #111827 100%)", "text": "#D1D5DB", "border": "#CD7F32"},
                4: {"bg": "linear-gradient(135deg, #374151 0%, #1F2937 100%)", "text": "#F3F4F6", "border": "#6B7280"}
            }
            
            config = tier_configs[tier]
            
            # COMPLETELY INLINE STYLES - NO CSS CLASSES TO AVOID STREAMLIT CONFLICTS
            st.markdown(f"""
            <div style="
                background: {config['bg']} !important;
                border: 2px solid {config['border']} !important;
                color: {config['text']} !important;
                padding: 1.5rem !important;
                margin: 0.5rem 0 !important;
                border-radius: 0.75rem !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="
                        background: {tier_badge_colors[tier]} !important;
                        color: {tier_badge_text[tier]} !important;
                        padding: 0.4rem 0.8rem !important;
                        border-radius: 1rem !important;
                        font-weight: bold !important;
                        font-size: 0.85rem !important;
                    ">
                        {tier_emojis[tier]} {tier_names[tier]} EVIDENCE
                    </span>
                </div>
                <div style="margin-bottom: 0.75rem;">
                    <strong style="color: {config['text']} !important;">Claim:</strong> 
                    <span style="color: {config['text']} !important; font-size: 1.05rem;">{claim}</span>
                </div>
                <div style="opacity: 0.9;">
                    <small style="color: {config['text']} !important;">📍 Source: {source}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        elif event_type == "objection_raised":
            st.markdown("""
            <div class="objection-splash" style="text-align: center; padding: 1rem;">
                ⚡ OBJECTION! ⚡
            </div>
            """, unsafe_allow_html=True)
            
            reason = event["content"].get("reason", "")
            st.warning(f"Objection: {reason}")
        
        elif event_type == "dramatic_moment":
            moment_type = event["content"].get("type", "")
            message = event["content"].get("message", "")
            
            st.markdown(f"""
            <div class="dramatic-moment">
                <h3 style="text-align: center;">🎭 {moment_type.replace('_', ' ').upper()} 🎭</h3>
                <p style="text-align: center; font-size: 1.2rem;">{message}</p>
            </div>
            """, unsafe_allow_html=True)
        
        elif event_type == "verdict_rendered":
            self.render_verdict(event["content"])
    
    def render_verdict(self, verdict_content: Dict):
        """Render the final verdict"""
        decision = verdict_content.get("verdict", "")
        confidence = verdict_content.get("confidence", 0)
        reasoning = verdict_content.get("reasoning", "")
        alternative = verdict_content.get("alternative", "")
        savings = verdict_content.get("savings", 0)
        
        # Verdict colors and emojis
        verdict_styles = {
            "APPROVED": {"color": "#10B981", "emoji": "✅", "bg": "#D1FAE5"},
            "REJECTED": {"color": "#EF4444", "emoji": "❌", "bg": "#FEE2E2"},
            "CONDITIONAL": {"color": "#F59E0B", "emoji": "⚠️", "bg": "#FEF3C7"},
            "NEEDS_RESEARCH": {"color": "#3B82F6", "emoji": "🔍", "bg": "#DBEAFE"}
        }
        
        style = verdict_styles.get(decision, verdict_styles["REJECTED"])
        
        st.markdown(f"""
        <div style="background: {style['bg']}; padding: 2rem; border-radius: 1rem; border: 3px solid {style['color']}; margin: 1rem 0;">
            <h1 style="text-align: center; color: {style['color']};">
                {style['emoji']} VERDICT: {decision} {style['emoji']}
            </h1>
            <h3 style="text-align: center;">Judge Confidence: {confidence:.1f}%</h3>
            <p style="margin-top: 1rem;"><strong>Reasoning:</strong> {reasoning}</p>
            {f'<p><strong>Alternative Suggestion:</strong> {alternative}</p>' if alternative else ''}
            {f'<h2 style="text-align: center; color: {style["color"]};">💰 Money Saved: ${savings:,.0f}</h2>' if savings > 0 else ''}
        </div>
        """, unsafe_allow_html=True)
        
        # Save to session state
        st.session_state.verdict = verdict_content
    
    async def run_debate_stream(self, requirement: str, config: Dict):
        """Run the debate with streaming updates"""
        # Create agents
        pro_team = create_pro_team()
        con_team = create_con_team()
        judge = create_judge(config["judge_type"])
        
        # Create orchestrator
        debate_config = {
            "max_rounds": config["max_rounds"],
            "enable_special_effects": config["enable_effects"],
            "streaming_delay": 0.5 if config["intensity"] == "Quick" else 1.0
        }
        
        orchestrator = DebateOrchestrator(
            pro_agents=pro_team,
            con_agents=con_team,
            judge_agent=judge,
            debate_config=debate_config
        )
        
        # Run debate with streaming
        event_placeholder = st.empty()
        
        async for event in orchestrator.analyze_requirement_streaming(requirement):
            # Update session state
            if event.get("type") == "phase_change":
                st.session_state.current_phase = event["content"]["phase"]
            elif event.get("type") == "confidence_update":
                st.session_state.pro_confidence = event["content"]["pro_confidence"]
                st.session_state.con_confidence = event["content"]["con_confidence"]
            elif event.get("type") == "final_result":
                st.session_state.verdict = event["data"]["verdict"]
                st.session_state.debate_active = False
            else:
                st.session_state.debate_events.append(event)
            
            # Update UI
            with event_placeholder.container():
                self.render_debate_arena()
            
            # Small delay for dramatic effect
            await asyncio.sleep(0.1)
    
    def run(self):
        """Main application entry point"""
        self.render_header()
        
        # Sidebar configuration
        config = self.render_sidebar()
        
        # Main content area
        requirement, analyze_button = self.render_requirement_input()
        
        st.divider()
        
        # Start debate if button clicked
        if analyze_button and requirement:
            st.session_state.debate_active = True
            st.session_state.debate_events = []
            st.session_state.verdict = None
            st.session_state.pro_confidence = 50
            st.session_state.con_confidence = 50
            
            # Run the debate
            with st.spinner("Agents are preparing for battle..."):
                # Note: Streamlit doesn't support async directly, so we'd need to handle this
                # In production, this would be handled via WebSocket or background task
                st.info("Debate simulation starting... (In production, this would stream in real-time)")
                
                # Simulate some debate events for demonstration
                self.simulate_debate(requirement)
        
        # Show debate arena if active or has history
        if st.session_state.debate_active or st.session_state.debate_events:
            self.render_debate_arena()
        
        # Show verdict if available
        if st.session_state.verdict:
            st.balloons()
    
    def simulate_debate(self, requirement: str):
        """Simulate a debate for demonstration"""
        # This is a simplified simulation for UI demonstration
        # In production, this would connect to the actual debate orchestrator
        
        import random
        
        # Simulate opening statements
        st.session_state.current_phase = "opening_statements"
        st.session_state.debate_events.append({
            "event_type": "agent_speaks",
            "agent": "Product Visionary",
            "content": {
                "team": "PRO",
                "argument": f"This {requirement} represents the future of our industry. Innovation requires bold moves!"
            }
        })
        
        st.session_state.debate_events.append({
            "event_type": "agent_speaks",
            "agent": "Senior Architect",
            "content": {
                "team": "CON",
                "argument": f"I've seen {requirement} fail spectacularly. The complexity alone will sink this project."
            }
        })
        
        # Simulate evidence presentation
        st.session_state.current_phase = "evidence_duel"
        st.session_state.debate_events.append({
            "event_type": "evidence_presented",
            "content": {
                "evidence": {
                    "tier": 2,
                    "claim": "Market research shows 73% of users want this feature",
                    "source": "Gartner Report 2024"
                },
                "team": "PRO"
            }
        })
        
        st.session_state.debate_events.append({
            "event_type": "evidence_presented",
            "content": {
                "evidence": {
                    "tier": 1,
                    "claim": "3 competitors removed similar features after poor adoption",
                    "source": "TechCrunch Post-Mortem Analysis"
                },
                "team": "CON"
            }
        })
        
        # Simulate objection
        st.session_state.debate_events.append({
            "event_type": "objection_raised",
            "agent": "QA Engineer",
            "content": {
                "reason": "That market research is from B2C, we're B2B!",
                "team": "CON"
            }
        })
        
        # Update confidence
        st.session_state.pro_confidence = 35
        st.session_state.con_confidence = 75
        
        # Simulate verdict
        st.session_state.current_phase = "judgment"
        st.session_state.debate_events.append({
            "event_type": "verdict_rendered",
            "content": {
                "verdict": "REJECTED",
                "confidence": 78.5,
                "reasoning": "The evidence strongly suggests this feature has failed in similar contexts. The implementation complexity and maintenance burden outweigh potential benefits.",
                "alternative": "Consider a simpler MVP focusing on core functionality first",
                "savings": 2100000
            }
        })


# Main execution
if __name__ == "__main__":
    app = DebateUI()
    app.run()
#built with love
