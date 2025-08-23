#!/usr/bin/env python3
"""
Debug version of the debate arena to test evidence card rendering
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Debug Debate Arena - Evidence Cards",
    page_icon="🔍",
    layout="wide"
)

# Same CSS as main app but with debug markers
st.markdown("""
<style>
    /* Dark theme for better contrast */
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
    
    /* AGGRESSIVE evidence tier styling - SAME AS MAIN APP */
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
    
    /* Additional fallback styling - SAME AS MAIN APP */
    div[class*="evidence-tier"] {
        background: #1F2937 !important;
        color: #F3F4F6 !important;
    }
    
    div[class*="evidence-tier"] * {
        color: inherit !important;
    }
    
    /* Aggressive override for any white backgrounds */
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
</style>
""", unsafe_allow_html=True)

def render_event_debug(event):
    """EXACT SAME METHOD as main app render_event() for evidence"""
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
        
        # Get tier-specific colors  
        tier_text_colors = {1: "#FFD700", 2: "#E5E7EB", 3: "#D1D5DB", 4: "#F3F4F6"}
        text_color = tier_text_colors[tier]
        
        st.markdown(f"""
        <div class="evidence-tier-{tier}" style="padding: 1.5rem !important; margin: 0.5rem 0 !important; border-radius: 0.75rem !important; box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important; background: #1F2937 !important;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <span style="background: {tier_badge_colors[tier]} !important; color: {tier_badge_text[tier]} !important; padding: 0.4rem 0.8rem !important; border-radius: 1rem !important; font-weight: bold !important; font-size: 0.85rem !important;">
                    {tier_emojis[tier]} {tier_names[tier]} EVIDENCE
                </span>
            </div>
            <div style="margin-bottom: 0.75rem;">
                <strong style="color: {text_color} !important;">Claim:</strong> 
                <span style="color: {text_color} !important; font-size: 1.05rem;">{claim}</span>
            </div>
            <div style="opacity: 0.9;">
                <small style="color: {text_color} !important;">📍 Source: {source}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

def simulate_debate_debug(requirement: str):
    """EXACT SAME SIMULATION as main app"""
    # Simulate evidence presentation - SAME DATA as main app
    evidence_events = [
        {
            "event_type": "evidence_presented",
            "content": {
                "evidence": {
                    "tier": 2,
                    "claim": "Market research shows 73% of users want this feature",
                    "source": "Gartner Report 2024"
                },
                "team": "PRO"
            }
        },
        {
            "event_type": "evidence_presented", 
            "content": {
                "evidence": {
                    "tier": 1,
                    "claim": "3 competitors removed similar features after poor adoption",
                    "source": "TechCrunch Post-Mortem Analysis"
                },
                "team": "CON"
            }
        }
    ]
    
    return evidence_events

# Initialize session state
if "debug_events" not in st.session_state:
    st.session_state.debug_events = []

# Header
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1>🔍 Debug Debate Arena</h1>
    <h3>Testing evidence cards in debate context</h3>
</div>
""", unsafe_allow_html=True)

# Input section
requirement = st.text_input("Enter requirement:", value="add blockchain into mobile banking app")

if st.button("🎯 Start Debug Debate"):
    st.session_state.debug_events = simulate_debate_debug(requirement)

# Evidence Section - SAME STRUCTURE as main app
if st.session_state.debug_events:
    st.markdown("""
    <div class="evidence-section-header">
        <h2 style="text-align: center; margin: 0; color: inherit;">📜 Debate Transcript</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Separate evidence events - SAME LOGIC as main app
    evidence_events = []
    for event in st.session_state.debug_events:
        if event.get("event_type") == "evidence_presented":
            evidence_events.append(event)
    
    if evidence_events:
        st.markdown("""
        <div class="evidence-section-header">
            <h3 style="text-align: center; margin: 0; color: inherit;">📊 Evidence Presented</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Render evidence - SAME METHOD as main app
        for event in evidence_events:
            render_event_debug(event)

# Debug information
st.markdown("---")
st.markdown("### 🔍 Debug Info:")
st.markdown(f"**Events in session state**: {len(st.session_state.debug_events)}")

if st.session_state.debug_events:
    st.markdown("**Event details**:")
    for i, event in enumerate(st.session_state.debug_events):
        st.json({f"Event {i+1}": event})

st.markdown("### ❓ Key Question:")
st.markdown("**If evidence cards show up here but NOT in main app, then there's a session state or rendering timing issue in the main app!**")
#built with love
