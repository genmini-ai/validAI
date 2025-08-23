#!/usr/bin/env python3
"""
Multi-Round Debate Streamlit Interface
Integrates with the multi-round debate API for real agent interactions
"""

import streamlit as st
import requests
import json
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

# Import config
try:
    from config import ReqDefenderConfig
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="ReqDefender - Multi-Round Debate Arena",
    page_icon="🎭",
    layout="wide"
)

# Enhanced CSS with debate-specific styles
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #F1F5F9;
    }
    
    .big-title {
        font-size: 3.5rem;
        text-align: center;
        color: #60A5FA;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #94A3B8;
        margin-bottom: 2rem;
        font-size: 1.2rem;
    }
    
    .round-header {
        background: linear-gradient(135deg, #3730A3 0%, #1E40AF 100%);
        color: #F1F5F9;
        padding: 1rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        text-align: center;
        border: 2px solid #60A5FA;
        box-shadow: 0 4px 15px rgba(96, 165, 250, 0.3);
    }
    
    .argument-card {
        background: linear-gradient(135deg, #1F2937 0%, #111827 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 0.75rem 0;
        border-left: 4px solid #60A5FA;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .pro-argument {
        border-left: 4px solid #10B981 !important;
        background: linear-gradient(135deg, #065F46 5%, #1F2937 100%);
    }
    
    .con-argument {
        border-left: 4px solid #EF4444 !important;
        background: linear-gradient(135deg, #991B1B 5%, #1F2937 100%);
    }
    
    .rebuttal-indicator {
        background: #3730A3;
        color: #F1F5F9;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
        display: inline-block;
    }
    
    .transcript-container {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 2px solid #8B5CF6;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        max-height: 600px;
        overflow-y: auto;
    }
    
    .closing-summary {
        background: linear-gradient(135deg, #7C2D12 0%, #92400E 100%);
        border: 2px solid #F59E0B;
        padding: 1.5rem;
        border-radius: 0.75rem;
        color: #FEF3C7;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }
    
    .verdict-approved {
        background: linear-gradient(135deg, #065F46 0%, #047857 100%);
        border: 2px solid #10B981;
        padding: 2rem;
        border-radius: 0.75rem;
        color: #D1FAE5;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        text-align: center;
    }
    
    .verdict-rejected {
        background: linear-gradient(135deg, #991B1B 0%, #DC2626 100%);
        border: 2px solid #EF4444;
        padding: 2rem;
        border-radius: 0.75rem;
        color: #FEE2E2;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        text-align: center;
    }
    
    .verdict-research {
        background: linear-gradient(135deg, #92400E 0%, #D97706 100%);
        border: 2px solid #F59E0B;
        padding: 2rem;
        border-radius: 0.75rem;
        color: #FEF3C7;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        text-align: center;
    }
    
    .debate-stats {
        background: linear-gradient(135deg, #1E40AF 0%, #3730A3 100%);
        border: 2px solid #60A5FA;
        color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(96, 165, 250, 0.3);
    }
    
    .debate-stats h3 {
        color: #DBEAFE !important;
        margin: 0 0 0.5rem 0 !important;
        font-size: 1.1rem !important;
    }
    
    .debate-stats p {
        color: #BFDBFE !important;
        margin: 0 !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
    }
    
    .debate-stats .metric-label {
        color: #DBEAFE !important;
        font-size: 0.9rem !important;
        font-weight: normal !important;
    }
</style>
""", unsafe_allow_html=True)

class MultiRoundDebateApp:
    """Streamlit app for multi-round debates"""
    
    def __init__(self):
        self.initialize_session_state()
        self.setup_api_config()
        
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        defaults = {
            "debate_active": False,
            "debate_transcript": None,
            "debate_result": None,
            "current_requirement": "",
            "api_available": False
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def setup_api_config(self):
        """Setup API configuration"""
        if CONFIG_AVAILABLE:
            config = ReqDefenderConfig.get_server_config()
            self.api_host = os.getenv("TEST_HOST", "localhost")
            self.api_port = config.get("debate_api_port", 8004)
        else:
            self.api_host = os.getenv("TEST_HOST", "localhost")
            self.api_port = int(os.getenv("DEBATE_API_PORT", 8004))
        
        self.api_url = f"http://{self.api_host}:{self.api_port}"
    
    def check_api_health(self):
        """Check if debate API is available"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("ai_available", False)
            return False
        except Exception:
            return False
    
    def render_header(self):
        """Render the application header"""
        st.markdown('<h1 class="big-title">🎭 ReqDefender</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Multi-Round AI Agent Debate Arena</p>', unsafe_allow_html=True)
        
        # API Status
        col1, col2, col3, col4 = st.columns(4)
        
        # Check API status synchronously for display
        def check_api_sync():
            try:
                import requests
                response = requests.get(f"{self.api_url}/health", timeout=2)
                return response.status_code == 200
            except:
                return False
        
        api_status = check_api_sync()
        st.session_state.api_available = api_status
        
        with col1:
            if api_status:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #065F46, #047857); 
                           border: 2px solid #10B981; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                    <h4 style="color: #D1FAE5; margin: 0;">🎭 Debate API</h4>
                    <p style="color: #A7F3D0; margin: 0; font-size: 1.2rem; font-weight: bold;">Online</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #991B1B, #DC2626); 
                           border: 2px solid #EF4444; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                    <h4 style="color: #FEE2E2; margin: 0;">🎭 Debate API</h4>
                    <p style="color: #FECACA; margin: 0; font-size: 1.2rem; font-weight: bold;">Offline</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1E40AF, #3730A3); 
                       border: 2px solid #60A5FA; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                <h4 style="color: #DBEAFE; margin: 0;">🌐 Server</h4>
                <p style="color: #BFDBFE; margin: 0; font-size: 1.2rem; font-weight: bold;">:{self.api_port}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if api_status:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #065F46, #047857); 
                           border: 2px solid #10B981; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                    <h4 style="color: #D1FAE5; margin: 0;">🤖 AI Agents</h4>
                    <p style="color: #A7F3D0; margin: 0; font-size: 1.2rem; font-weight: bold;">Ready</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #92400E, #D97706); 
                           border: 2px solid #F59E0B; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                    <h4 style="color: #FEF3C7; margin: 0;">🤖 AI Agents</h4>
                    <p style="color: #FDE68A; margin: 0; font-size: 1.2rem; font-weight: bold;">Waiting</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #7C2D12, #92400E); 
                       border: 2px solid #F59E0B; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                <h4 style="color: #FEF3C7; margin: 0;">🔄 Max Rounds</h4>
                <p style="color: #FDE68A; margin: 0; font-size: 1.2rem; font-weight: bold;">2-4</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
    
    def render_sidebar(self):
        """Render configuration sidebar"""
        with st.sidebar:
            st.header("⚙️ Debate Configuration")
            
            # Debate settings
            num_rounds = st.select_slider(
                "Number of Debate Rounds",
                options=[2, 3, 4],
                value=3,
                help="More rounds = deeper analysis but longer processing time"
            )
            
            # Advanced settings
            st.subheader("📊 Advanced Settings")
            
            show_transcript = st.checkbox(
                "Show Full Transcript",
                value=True,
                help="Display round-by-round debate progression"
            )
            
            show_references = st.checkbox(
                "Show Rebuttal References",
                value=True,
                help="Highlight which points agents are responding to"
            )
            
            auto_refresh = st.checkbox(
                "Auto-refresh Results",
                value=False,
                help="Automatically refresh the page after debate completes"
            )
            
            st.markdown("---")
            
            # Debate explanation
            st.subheader("🎯 How Multi-Round Debates Work")
            st.markdown("""
            **Round 1 - Opening Statements**
            - PRO & CON teams present initial arguments
            - Based on gathered evidence
            
            **Round 2+ - Rebuttals**
            - Agents respond to opponent's points
            - Reference specific arguments to counter
            
            **Final - Closing Statements**
            - Teams summarize their position
            - Judge evaluates entire debate
            """)
            
            return {
                "num_rounds": num_rounds,
                "show_transcript": show_transcript,
                "show_references": show_references,
                "auto_refresh": auto_refresh
            }
    
    def render_requirement_input(self):
        """Render requirement input section"""
        st.markdown("### 📝 Enter Your Requirement for Multi-Round Debate")
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            requirement = st.text_area(
                "What feature or requirement should be debated?",
                placeholder="e.g., 'Implement AI-powered code review system', 'Add blockchain authentication'",
                height=120,
                key="requirement_input"
            )
        
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            start_button = st.button(
                "🚀 Start Multi-Round Debate",
                type="primary",
                use_container_width=True,
                disabled=st.session_state.debate_active or not st.session_state.api_available
            )
        
        if not st.session_state.api_available:
            st.error(f"❌ Debate API is not available at {self.api_url}")
            st.info("Make sure to run: `python3 api_debate.py`")
        
        # Simplified example requirements - remove the problematic HTML approach
        # Just provide inspiration text instead of complex buttons
        with st.expander("💡 Need inspiration? Click for example requirements", expanded=False):
            st.markdown("""
            **Popular debate topics:**
            - "Add real-time collaborative editing to our IDE"
            - "Migrate monolith to microservices architecture"  
            - "Implement blockchain-based user authentication"
            - "Replace REST API with GraphQL endpoints"
            
            *Copy any example above and paste it into the text area*
            """)
        
        return requirement, start_button
    
    def render_debate_transcript(self, transcript, config):
        """Render the complete debate transcript with progressive loading"""
        if not transcript or not config["show_transcript"]:
            return
        
        transcript_data = transcript["transcript"]
        rounds = transcript_data["rounds"]
        
        # Progressive loading controls
        st.markdown("## 📜 Interactive Debate Transcript")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("**Navigate through the debate rounds:**")
        with col2:
            # Custom styled Show All button
            st.markdown("""
            <style>
            .control-button-show {
                background: linear-gradient(135deg, #059669 0%, #047857 100%);
                border: 2px solid #10B981;
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 0.375rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                width: 100%;
                text-align: center;
            }
            .control-button-show:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
            }
            </style>
            """, unsafe_allow_html=True)
            show_all = st.button("📖 Show All Rounds", key="show_all_rounds", type="primary")
            
        with col3:
            # Custom styled Collapse All button
            st.markdown("""
            <style>
            .control-button-collapse {
                background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%);
                border: 2px solid #EF4444;
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 0.375rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                width: 100%;
                text-align: center;
            }
            .control-button-collapse:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
            }
            </style>
            """, unsafe_allow_html=True)
            collapse_all = st.button("📕 Collapse All", key="collapse_all_rounds", type="secondary")
        
        # Initialize session state for round visibility
        if "round_visibility" not in st.session_state:
            st.session_state.round_visibility = {i: i == 1 for i in range(1, len(rounds) + 1)}
        
        if show_all:
            st.session_state.round_visibility = {i: True for i in range(1, len(rounds) + 1)}
        elif collapse_all:
            st.session_state.round_visibility = {i: False for i in range(1, len(rounds) + 1)}
        
        # Simple timeline with native Streamlit buttons
        st.markdown("### 🕐 Debate Timeline")
        
        timeline_cols = st.columns(len(rounds))
        for i, (col, round_data) in enumerate(zip(timeline_cols, rounds)):
            round_num = round_data["round_number"]
            round_type = round_data["round_type"].replace("_", " ").title()
            is_visible = st.session_state.round_visibility.get(round_num, False)
            
            with col:
                # Determine button style based on round type and visibility
                if round_data["round_type"] == "opening":
                    button_type = "primary" if is_visible else "secondary"
                elif "rebuttal" in round_data["round_type"]:
                    button_type = "primary" if is_visible else "secondary"
                else:  # closing
                    button_type = "primary" if is_visible else "secondary"
                
                status_icon = "🔽" if is_visible else "▶️"
                button_label = f"{status_icon} Round {round_num}\n{round_type}"
                
                if st.button(button_label, key=f"timeline_btn_{round_num}", 
                           type=button_type, use_container_width=True,
                           help=f"Toggle Round {round_num} visibility"):
                    st.session_state.round_visibility[round_num] = not st.session_state.round_visibility[round_num]
        
        st.markdown("---")
        
        # Progressive round display
        with st.container():
            st.markdown('<div class="transcript-container">', unsafe_allow_html=True)
            
            for round_data in rounds:
                round_num = round_data["round_number"]
                round_type = round_data["round_type"].replace("_", " ").title()
                
                # Round header (always visible)
                is_visible = st.session_state.round_visibility.get(round_num, False)
                expand_icon = "🔽" if is_visible else "▶️"
                
                round_header_html = f"""
                <div class="round-header" style="cursor: pointer;">
                    <h3>{expand_icon} Round {round_num}: {round_type}</h3>
                    <p style="margin: 0; opacity: 0.8; font-size: 0.9rem;">
                        Click to {'collapse' if is_visible else 'expand'} • 
                        {len(round_data.get('pro_arguments', []))} PRO arguments • 
                        {len(round_data.get('con_arguments', []))} CON arguments
                    </p>
                </div>
                """
                
                # Make header clickable
                st.markdown(round_header_html, unsafe_allow_html=True)
                
                # Interactive round header (clickable)
                toggle_button_style = "🔽 Collapse" if is_visible else "▶️ Expand"
                button_color = "#059669" if is_visible else "#3730A3"  # Green when expanded, blue when collapsed
                
                st.markdown(f"""
                <style>
                .round-toggle-btn {{
                    background: linear-gradient(135deg, {button_color} 0%, {button_color}CC 100%);
                    border: none;
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 0.375rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                    margin: 0.5rem 0;
                    width: 100%;
                }}
                .round-toggle-btn:hover {{
                    transform: translateY(-1px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }}
                </style>
                """, unsafe_allow_html=True)
                
                if st.button(f"{toggle_button_style} Round {round_num}", 
                           key=f"toggle_round_{round_num}",
                           help=f"{'Hide' if is_visible else 'Show'} Round {round_num} arguments"):
                    st.session_state.round_visibility[round_num] = not st.session_state.round_visibility[round_num]
                
                # Show round content if visible
                if st.session_state.round_visibility.get(round_num, False):
                    # Arguments in columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 💚 PRO Team")
                        for i, arg in enumerate(round_data["pro_arguments"], 1):
                            # Show rebuttal references if available
                            ref_text = ""
                            if config["show_references"] and round_data.get("pro_references_con"):
                                refs = round_data["pro_references_con"]
                                if refs:
                                    ref_text = f'<div class="rebuttal-indicator">↪️ Responds to: {refs[0][:50]}...</div>'
                            
                            with st.expander(f"PRO Argument {i}", expanded=(i == 1)):
                                st.markdown(f"""
                                <div class="argument-card pro-argument">
                                    {ref_text}
                                    <strong>PRO Agent {i}:</strong><br>
                                    {arg}
                                </div>
                                """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("#### ❌ CON Team")
                        for i, arg in enumerate(round_data["con_arguments"], 1):
                            # Show rebuttal references if available
                            ref_text = ""
                            if config["show_references"] and round_data.get("con_references_pro"):
                                refs = round_data["con_references_pro"]
                                if refs:
                                    ref_text = f'<div class="rebuttal-indicator">↪️ Responds to: {refs[0][:50]}...</div>'
                            
                            with st.expander(f"CON Argument {i}", expanded=(i == 1)):
                                st.markdown(f"""
                                <div class="argument-card con-argument">
                                    {ref_text}
                                    <strong>CON Agent {i}:</strong><br>
                                    {arg}
                                </div>
                                """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                
                else:
                    # Show collapsed summary
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #374151 0%, #1F2937 100%); 
                               padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; 
                               border-left: 4px solid #60A5FA;">
                        <em>Round {round_num} collapsed - Click "Toggle Round {round_num}" above to expand</em>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_closing_statements(self, transcript):
        """Render final closing statements with collapse controls"""
        if not transcript:
            return
        
        transcript_data = transcript["transcript"]
        summaries = transcript_data.get("final_summaries", {})
        
        if not summaries:
            return
        
        # Initialize session state for closing statements visibility
        if "show_closing_statements" not in st.session_state:
            st.session_state.show_closing_statements = True
        
        # Header with toggle control
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("## 🎤 Closing Statements")
        with col2:
            toggle_text = "🔽 Hide" if st.session_state.show_closing_statements else "▶️ Show"
            button_type = "secondary" if st.session_state.show_closing_statements else "primary"
            if st.button(f"{toggle_text} Closing", key="toggle_closing", type=button_type):
                st.session_state.show_closing_statements = not st.session_state.show_closing_statements
        
        if st.session_state.show_closing_statements:
            # Expandable closing statements
            with st.expander("💚 PRO Team Final Statement", expanded=True):
                if "PRO" in summaries:
                    st.markdown(f"""
                    <div class="closing-summary" style="border-left: 4px solid #10B981;">
                        {summaries["PRO"]}
                    </div>
                    """, unsafe_allow_html=True)
            
            with st.expander("❌ CON Team Final Statement", expanded=True):
                if "CON" in summaries:
                    st.markdown(f"""
                    <div class="closing-summary" style="border-left: 4px solid #EF4444;">
                        {summaries["CON"]}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #374151 0%, #1F2937 100%); 
                       padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; 
                       border-left: 4px solid #F59E0B;">
                <em>🎤 Closing statements hidden - Click "Show Closing" above to view final arguments</em>
            </div>
            """, unsafe_allow_html=True)
    
    def render_final_verdict(self, result):
        """Render the final judge verdict with progressive reveal"""
        if not result or not result.get("transcript"):
            return
        
        verdict = result["transcript"]["judge_verdict"]
        
        # Initialize session state for verdict details visibility
        if "show_verdict_details" not in st.session_state:
            st.session_state.show_verdict_details = False
        
        st.markdown("## ⚖️ Judge's Final Verdict")
        
        # Verdict display
        verdict_type = verdict["verdict"]
        confidence = verdict["confidence"]
        # Handle both API formats: full debate has 'reasoning', quick debate has 'summary'
        reasoning = verdict.get("reasoning") or verdict.get("summary", "No reasoning provided")
        
        # Main verdict (always visible)
        if verdict_type == "APPROVED":
            st.markdown(f"""
            <div class="verdict-approved">
                <h2>✅ APPROVED ✅</h2>
                <h3>Confidence: {confidence:.1f}%</h3>
                <p><strong>Judge's Reasoning:</strong></p>
                <p>{reasoning}</p>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()
            
        elif verdict_type == "REJECTED":
            st.markdown(f"""
            <div class="verdict-rejected">
                <h2>❌ REJECTED ❌</h2>
                <h3>Confidence: {confidence:.1f}%</h3>
                <p><strong>Judge's Reasoning:</strong></p>
                <p>{reasoning}</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:  # NEEDS_RESEARCH
            st.markdown(f"""
            <div class="verdict-research">
                <h2>🔍 NEEDS MORE RESEARCH 🔍</h2>
                <h3>Confidence: {confidence:.1f}%</h3>
                <p><strong>Judge's Reasoning:</strong></p>
                <p>{reasoning}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed analysis toggle
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 📊 Detailed Analysis")
        with col2:
            detail_text = "🔽 Hide Details" if st.session_state.show_verdict_details else "▶️ Show Details"
            button_type = "secondary" if st.session_state.show_verdict_details else "primary"
            if st.button(detail_text, key="toggle_verdict_details", type=button_type):
                st.session_state.show_verdict_details = not st.session_state.show_verdict_details
        
        if st.session_state.show_verdict_details:
            # Progressive reveal of verdict details
            if verdict.get("winning_arguments"):
                with st.expander("✅ Winning Arguments", expanded=False):
                    for i, arg in enumerate(verdict["winning_arguments"], 1):
                        st.markdown(f"**{i}.** {arg}")
            
            if verdict.get("losing_weaknesses"):
                with st.expander("⚠️ Losing Side Weaknesses", expanded=False):
                    for i, weak in enumerate(verdict["losing_weaknesses"], 1):
                        st.markdown(f"**{i}.** {weak}")
            
            if verdict.get("decisive_factors"):
                with st.expander("🎯 Decisive Factors", expanded=True):
                    st.markdown(f"**Key factors that influenced the decision:**")
                    st.markdown(f"{verdict['decisive_factors']}")
        
        else:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #374151 0%, #1F2937 100%); 
                       padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; 
                       border-left: 4px solid #60A5FA;">
                <em>📊 Detailed analysis hidden - Click "Show Details" above to see winning arguments, weaknesses, and decisive factors</em>
            </div>
            """, unsafe_allow_html=True)
    
    def render_debate_stats(self, result):
        """Render debate statistics"""
        if not result:
            return
        
        st.markdown("### 📊 Debate Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="debate-stats">
                <h3>🔄 Total Rounds</h3>
                <p>{result.get("total_rounds", 0)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="debate-stats">
                <h3>⏱️ Duration</h3>
                <p>{result.get('duration_seconds', 0):.1f}s</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            verdict = result.get("verdict", "Unknown")
            verdict_color = "#10B981" if verdict == "APPROVED" else "#EF4444" if verdict == "REJECTED" else "#F59E0B"
            st.markdown(f"""
            <div class="debate-stats">
                <h3>⚖️ Verdict</h3>
                <p style="color: {verdict_color} !important;">{verdict}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            confidence = result.get('confidence', 0)
            conf_color = "#10B981" if confidence >= 80 else "#F59E0B" if confidence >= 60 else "#EF4444"
            st.markdown(f"""
            <div class="debate-stats">
                <h3>📊 Confidence</h3>
                <p style="color: {conf_color} !important;">{confidence:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
    
    def run_debate_process(self, requirement: str, config: dict):
        """Run the complete debate process"""
        st.session_state.debate_active = True
        st.session_state.current_requirement = requirement
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.info("🚀 Starting multi-round debate...")
            progress_bar.progress(0.1)
            
            # Use synchronous requests instead of async
            import requests
            import json
            
            request_data = {
                "requirement": requirement,
                "num_rounds": config["num_rounds"]
            }
            
            # Make synchronous API call
            response = requests.post(
                f"{self.api_url}/debate",
                json=request_data,
                timeout=120  # 2 minutes timeout
            )
            
            progress_bar.progress(0.9)
            
            if response.status_code != 200:
                st.error(f"❌ Debate failed: {response.status_code} - {response.text}")
                return
            
            result = response.json()
            
            if "error" in result:
                st.error(f"❌ Debate failed: {result['error']}")
                return
            
            progress_bar.progress(1.0)
            status_text.success(f"✅ Debate completed in {result.get('duration_seconds', 0):.1f} seconds!")
            
            # Store results
            st.session_state.debate_result = result
            st.session_state.debate_transcript = result
            
            # Auto-refresh if enabled
            if config["auto_refresh"]:
                time.sleep(1)
                st.rerun()
            
        except requests.exceptions.Timeout:
            st.error("❌ Debate timed out. Try reducing the number of rounds.")
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Cannot connect to debate API at {self.api_url}")
            st.info("Make sure to run: `python3 api_debate.py`")
        except Exception as e:
            st.error(f"❌ Debate process failed: {e}")
            
        finally:
            st.session_state.debate_active = False
    
    def run(self):
        """Main application entry point"""
        self.render_header()
        
        # Sidebar configuration
        config = self.render_sidebar()
        
        # Main content
        requirement, start_button = self.render_requirement_input()
        
        # Start debate
        if start_button and requirement and st.session_state.api_available:
            # Clear previous results
            st.session_state.debate_result = None
            st.session_state.debate_transcript = None
            
            self.run_debate_process(requirement, config)
        
        # Show active debate status
        if st.session_state.debate_active:
            st.info(f"🎭 Multi-round debate in progress for: {st.session_state.current_requirement}")
        
        # Display results with progressive loading
        if st.session_state.debate_result and not st.session_state.debate_active:
            result = st.session_state.debate_result
            
            # Quick Summary (always visible)
            st.markdown("## 📋 Quick Summary")
            verdict_color = "#10B981" if result.get("verdict") == "APPROVED" else "#EF4444" if result.get("verdict") == "REJECTED" else "#F59E0B"
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1E40AF 0%, #3730A3 100%); 
                       border: 2px solid #60A5FA; padding: 1.5rem; border-radius: 0.75rem; margin: 1rem 0;">
                <h3 style="color: #FFFFFF; margin: 0 0 0.5rem 0;">
                    ⚖️ <span style="color: {verdict_color};">{result.get("verdict", "Unknown")}</span> 
                    with {result.get("confidence", 0):.1f}% confidence
                </h3>
                <p style="color: #DBEAFE; margin: 0;">
                    🕐 {result.get("total_rounds", 0)} rounds completed in {result.get("duration_seconds", 0):.1f} seconds
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Progressive content sections
            st.markdown("### 🔍 Explore Details")
            
            # Create tabs for organized content
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Statistics", 
                "📜 Round-by-Round", 
                "🎤 Final Statements", 
                "⚖️ Judge's Decision"
            ])
            
            with tab1:
                st.markdown("#### Debate Performance Metrics")
                self.render_debate_stats(result)
            
            with tab2:
                st.markdown("#### Interactive Debate Transcript")
                self.render_debate_transcript(result, config)
            
            with tab3:
                st.markdown("#### Team Closing Arguments")
                self.render_closing_statements(result)
            
            with tab4:
                st.markdown("#### Final Verdict & Analysis")
                self.render_final_verdict(result)
            
            # Restart option
            if st.button("🔄 Start New Debate", type="secondary"):
                st.session_state.debate_result = None
                st.session_state.debate_transcript = None
                st.session_state.current_requirement = ""
                st.rerun()

def main():
    """Application entry point"""
    app = MultiRoundDebateApp()
    app.run()

if __name__ == "__main__":
    main()
#built with love
