#!/usr/bin/env python3
"""
Test the evidence card visibility fix in isolation
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Evidence Card Fix Test",
    page_icon="🔧",
    layout="wide"
)

# Enhanced CSS with aggressive overrides
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
    
    /* Aggressive evidence tier styling with !important */
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
</style>
""", unsafe_allow_html=True)

def render_evidence_card_fixed(tier, claim, source):
    """Render evidence card with the exact same method as the main app"""
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

# Header
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1>🔧 Evidence Card Visibility Fix Test</h1>
    <h3>Testing the exact CSS/HTML from the main application</h3>
</div>
""", unsafe_allow_html=True)

# Evidence Section Header (same as main app)
st.markdown("""
<div class="evidence-section-header">
    <h3 style="text-align: center; margin: 0; color: inherit;">📊 Evidence Presented</h3>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🧪 Same rendering method as main app:")

# Test all evidence tiers with the exact same rendering code
col1, col2 = st.columns(2)

with col1:
    render_evidence_card_fixed(
        tier=2,
        claim="Market research shows 73% want this feature", 
        source="Gartner Report 2024"
    )
    
    render_evidence_card_fixed(
        tier=4,
        claim="Some developers think this could work",
        source="Reddit discussion"
    )

with col2:
    render_evidence_card_fixed(
        tier=1,
        claim="3 competitors removed similar features after poor adoption",
        source="TechCrunch Post-Mortem Analysis" 
    )
    
    render_evidence_card_fixed(
        tier=3,
        claim="Blog posts show mixed implementation results",
        source="Various tech blogs"
    )

st.markdown("---")

# Debug info
st.markdown("### 🔍 Debug Information:")
st.markdown("""
**CSS Changes Made:**
1. Added `!important` to all CSS rules
2. Used explicit color values instead of `color: inherit`  
3. Added aggressive background overrides for all child elements
4. Increased CSS specificity with multiple selectors
5. Added fallback background colors

**Key Issue Identified:**
- Streamlit's default CSS was overriding our custom styles
- White backgrounds were being applied by Streamlit's internal styling
- Text color inheritance was failing due to CSS cascade conflicts
""")

if st.button("🧪 If you can see this evidence clearly, the fix works!"):
    st.balloons()
    st.success("✅ Evidence cards are now visible! The CSS fix is working correctly.")
    st.info("The main application will now have properly visible evidence cards.")
#built with love
