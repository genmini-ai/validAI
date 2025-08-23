#!/usr/bin/env python3
"""
Simplified Streamlit app with FIXED evidence card rendering
This reproduces the exact same debate arena flow as the main app
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="ReqDefender - Fixed Evidence Cards",
    page_icon="🛡️",
    layout="wide"
)

# Basic CSS (keeping the overall theme but not relying on classes for evidence)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #F1F5F9;
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
</style>
""", unsafe_allow_html=True)

def render_event(event):
    """EXACT SAME render_event method as main app with FIXED inline styles"""
    event_type = event.get("event_type", "")
    
    if event_type == "evidence_presented":
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

def simulate_debate(requirement: str):
    """EXACT SAME simulate_debate as main app"""
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

def render_debate_arena():
    """EXACT SAME debate arena rendering as main app"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 1rem; margin: 1rem 0; border: 2px solid rgba(255, 255, 255, 0.1);">
        <h2 style="text-align: center; color: white;">⚔️ DEBATE ARENA ⚔️</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Event stream
    if st.session_state.debate_events:
        st.markdown("""
        <div class="evidence-section-header">
            <h2 style="text-align: center; margin: 0; color: inherit;">📜 Debate Transcript</h2>
        </div>
        """, unsafe_allow_html=True)
        
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
                render_event(event)

# Initialize session state
if "debate_active" not in st.session_state:
    st.session_state.debate_active = False
if "debate_events" not in st.session_state:
    st.session_state.debate_events = []

# Header
st.markdown("""
<div style="text-align: center;">
    <h1>🛡️ ReqDefender - FIXED VERSION</h1>
    <h3>Testing evidence card fix in actual debate arena</h3>
    <p style="color: #666;">This uses the EXACT same code path as the main app</p>
</div>
""", unsafe_allow_html=True)

# Input section
col1, col2 = st.columns([4, 1])

with col1:
    requirement = st.text_area(
        "What feature or requirement should we debate?",
        placeholder="e.g., 'Add blockchain to our todo app'",
        height=100,
        value="add blockchain into mobile banking app"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_button = st.button(
        "🎯 Start Debate",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.debate_active
    )

st.divider()

# Start debate if button clicked - EXACT SAME LOGIC as main app
if analyze_button and requirement:
    st.session_state.debate_active = True
    st.session_state.debate_events = []
    
    with st.spinner("Agents are preparing for battle..."):
        st.info("Debate simulation starting...")
        simulate_debate(requirement)

# Show debate arena if active or has history - EXACT SAME LOGIC as main app
if st.session_state.debate_active or st.session_state.debate_events:
    render_debate_arena()

# Debug info
if st.session_state.debate_events:
    with st.expander("🔍 Debug Info"):
        st.markdown(f"**Events in session**: {len(st.session_state.debate_events)}")
        for i, event in enumerate(st.session_state.debate_events):
            if event.get("event_type") == "evidence_presented":
                evidence = event["content"]["evidence"]
                st.markdown(f"**Event {i+1}**: Tier {evidence['tier']} - {evidence['claim'][:50]}...")

st.markdown("---")
st.markdown("### ✅ Expected Result:")
st.markdown("Evidence cards should now show **dark colored backgrounds** with **clearly visible text** - no more white boxes!")
#built with love
