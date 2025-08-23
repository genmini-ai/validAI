#!/usr/bin/env python3
"""
Test file for UI improvements - shows evidence cards with improved styling
"""

import streamlit as st
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="ReqDefender UI Test - Evidence Cards",
    page_icon="🛡️",
    layout="wide"
)

# Enhanced CSS with fixed evidence card styling
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
    
    .evidence-tier-1 {
        background: linear-gradient(135deg, #2D1B69 0%, #1F1347 100%);
        border: 2px solid #FFD700;
        color: #FFD700;
    }
    
    .evidence-tier-2 {
        background: linear-gradient(135deg, #4C1D95 0%, #2D1B69 100%);
        border: 2px solid #C0C0C0;
        color: #E5E7EB;
    }
    
    .evidence-tier-3 {
        background: linear-gradient(135deg, #1F2937 0%, #111827 100%);
        border: 2px solid #CD7F32;
        color: #D1D5DB;
    }
    
    .evidence-tier-4 {
        background: linear-gradient(135deg, #374151 0%, #1F2937 100%);
        border: 1px solid #6B7280;
        color: #F3F4F6;
    }
</style>
""", unsafe_allow_html=True)

def render_evidence_card(tier, claim, source):
    """Render an evidence card with the new styling"""
    tier_names = {1: "PLATINUM", 2: "GOLD", 3: "SILVER", 4: "BRONZE"}
    tier_badge_colors = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32", 4: "#6B7280"}
    tier_badge_text = {1: "#000", 2: "#000", 3: "#FFF", 4: "#FFF"}
    tier_emojis = {1: "💎", 2: "🥇", 3: "🥈", 4: "🥉"}
    
    st.markdown(f"""
    <div class="evidence-tier-{tier}" style="padding: 1.5rem; margin: 0.5rem 0; border-radius: 0.75rem; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <span style="background: {tier_badge_colors[tier]}; color: {tier_badge_text[tier]}; padding: 0.4rem 0.8rem; border-radius: 1rem; font-weight: bold; font-size: 0.85rem;">
                {tier_emojis[tier]} {tier_names[tier]} EVIDENCE
            </span>
        </div>
        <div style="margin-bottom: 0.75rem;">
            <strong style="color: inherit;">Claim:</strong> 
            <span style="color: inherit; font-size: 1.05rem;">{claim}</span>
        </div>
        <div style="opacity: 0.8;">
            <small style="color: inherit;">📍 Source: {source}</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_agent_card(team, agent_name, argument):
    """Render an agent statement card"""
    team_color = "#10B981" if team == "PRO" else "#EF4444"
    team_class = "pro-team" if team == "PRO" else "con-team"
    
    st.markdown(f"""
    <div class="agent-card {team_class}">
        <strong style="color: {team_color};">{agent_name}</strong>
        <p style="color: inherit; margin-top: 0.5rem;">{argument}</p>
    </div>
    """, unsafe_allow_html=True)

# Main UI
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1>🛡️ ReqDefender UI Test</h1>
    <h3>Testing Improved Evidence Card Visibility</h3>
</div>
""", unsafe_allow_html=True)

# Test Evidence Section
st.markdown("""
<div class="evidence-section-header">
    <h2 style="text-align: center; margin: 0; color: inherit;">📊 Evidence Presented</h2>
    <p style="text-align: center; margin: 0.5rem 0 0 0; opacity: 0.8;">Testing improved visibility and contrast</p>
</div>
""", unsafe_allow_html=True)

# Sample evidence cards of different tiers
col1, col2 = st.columns(2)

with col1:
    render_evidence_card(
        tier=1, 
        claim="Stanford research shows 95% performance improvement with this approach", 
        source="Stanford AI Research Paper 2024"
    )
    
    render_evidence_card(
        tier=3, 
        claim="Multiple tech blogs report successful implementations", 
        source="Various tech blogs"
    )

with col2:
    render_evidence_card(
        tier=2, 
        claim="Gartner predicts this will be industry standard by 2025", 
        source="Gartner Technology Trends 2024"
    )
    
    render_evidence_card(
        tier=4, 
        claim="Some developers on Reddit think this could work", 
        source="Reddit r/programming discussion"
    )

# Test Agent Cards
st.markdown("""
<div class="evidence-section-header">
    <h2 style="text-align: center; margin: 0; color: inherit;">💬 Agent Statements</h2>
    <p style="text-align: center; margin: 0.5rem 0 0 0; opacity: 0.8;">Testing agent card styling</p>
</div>
""", unsafe_allow_html=True)

render_agent_card(
    team="PRO",
    agent_name="💚 Product Visionary", 
    argument="This feature represents the future of our industry! The evidence clearly shows massive performance gains and user satisfaction improvements. We'd be crazy not to implement this game-changing technology."
)

render_agent_card(
    team="CON", 
    agent_name="❤️ Senior Architect",
    argument="I've seen this exact approach fail spectacularly at three different companies. The complexity alone will sink us, and the maintenance burden will consume our entire engineering budget for the next two years."
)

# Comparison section
st.markdown("""
<div class="evidence-section-header">
    <h2 style="text-align: center; margin: 0; color: inherit;">✅ UI Improvements Made</h2>
</div>
""", unsafe_allow_html=True)

improvements = [
    "🎨 **Dark theme**: Better contrast against dark backgrounds",
    "💎 **Evidence tier colors**: Each tier has distinct dark background with proper text contrast",
    "🏷️ **Tier badges**: Clear visual indicators with emojis and contrasting colors", 
    "📦 **Card shadows**: Enhanced depth and hover effects",
    "🎯 **Color inheritance**: Text properly inherits card colors",
    "📱 **Responsive design**: Better spacing and typography",
    "⚡ **Section headers**: Clear visual separation with styled headers"
]

for improvement in improvements:
    st.markdown(improvement)

st.markdown("---")
st.success("✅ Evidence cards should now be clearly visible with proper contrast!")
st.info("💡 The white text visibility issue has been resolved with dark card backgrounds and explicit color styling.")
#built with love
