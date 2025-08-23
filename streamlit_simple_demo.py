#!/usr/bin/env python3
"""Simplified Streamlit interface for ReqDefender"""

import streamlit as st
import random
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="ReqDefender - Agent Debate Arena",
    page_icon="🛡️",
    layout="wide"
)

# CSS for styling
st.markdown("""
<style>
    .big-title {
        font-size: 3rem;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .verdict-approved {
        background: #d1fae5;
        border: 2px solid #10b981;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #065f46;
    }
    .verdict-rejected {
        background: #fee2e2;
        border: 2px solid #ef4444;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #991b1b;
    }
    .evidence-card {
        background: linear-gradient(135deg, #1F2937 0%, #111827 100%) !important;
        border: 2px solid #3B82F6 !important;
        color: #F3F4F6 !important;
        padding: 1rem;
        border-radius: 0.5rem;
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
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="big-title">🛡️ ReqDefender</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI Agents Debate Your Requirements to Death</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        judge_type = st.selectbox(
            "Judge Personality",
            ["Pragmatist", "Innovator", "User Advocate"],
            help="Different judges have different biases"
        )
        
        intensity = st.select_slider(
            "Debate Intensity",
            options=["Quick", "Standard", "Deep"],
            value="Standard"
        )
        
        st.markdown("---")
        st.subheader("🎭 The Agents")
        
        st.markdown("**PRO Team (Advocates) 💚**")
        st.markdown("🎯 Product Visionary  \n💰 Sales Champion  \n🎨 UX Designer")
        
        st.markdown("**CON Team (Skeptics) ❤️**")
        st.markdown("🏗️ Senior Architect  \n🔍 QA Engineer  \n📊 Data Analyst")
    
    # Main interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        requirement = st.text_area(
            "What feature or requirement should we debate?",
            placeholder="e.g., 'Add blockchain to our todo app', 'Implement AI-powered code review'",
            height=100
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_button = st.button("🎯 Start Debate", type="primary", use_container_width=True)
    
    # Example buttons
    st.markdown("**Try these examples:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💡 Add blockchain to our todo app"):
            st.session_state.example_requirement = "Add blockchain to our todo app"
    
    with col2:
        if st.button("💡 Implement real-time collaboration"):
            st.session_state.example_requirement = "Implement real-time collaboration"
    
    with col3:
        if st.button("💡 Build AI chatbot for support"):
            st.session_state.example_requirement = "Build AI chatbot for customer support"
    
    # Use example if clicked
    if hasattr(st.session_state, 'example_requirement'):
        requirement = st.session_state.example_requirement
        del st.session_state.example_requirement
        st.rerun()
    
    if analyze_button and requirement:
        run_debate_simulation(requirement, judge_type, intensity)

def run_debate_simulation(requirement: str, judge_type: str, intensity: str):
    """Run a simulated debate"""
    
    st.markdown("---")
    st.markdown("## ⚔️ Debate Arena")
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Simulate debate phases
    phases = [
        ("🎭 Pre-Battle", "Agents preparing arguments..."),
        ("📢 Opening Statements", "Teams present their initial positions..."),
        ("⚔️ Evidence Duel", "Rapid-fire evidence exchange!"),
        ("🎯 Cross-Examination", "Critical questions and challenges..."),
        ("🏁 Final Arguments", "Last chance to convince the judge..."),
        ("⚖️ Judgment", "Judge deliberating...")
    ]
    
    # Debate visualization
    debate_container = st.container()
    
    for i, (phase, description) in enumerate(phases):
        progress_bar.progress((i + 1) / len(phases))
        status_text.text(f"{phase}: {description}")
        
        with debate_container:
            if i == 0:  # Pre-battle
                st.info(f"🎭 **Analyzing requirement:** {requirement}")
            
            elif i == 1:  # Opening statements
                col1, col2 = st.columns(2)
                with col1:
                    st.success("💚 **Product Visionary**: This represents the future of our industry! Innovation requires bold moves like this.")
                with col2:
                    st.error("❤️ **Senior Architect**: I've seen this fail spectacularly before. The complexity alone will sink us.")
            
            elif i == 2:  # Evidence duel
                st.markdown("### 📊 Evidence Presented")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    <div class="evidence-card">
                    <strong>🥈 SILVER EVIDENCE</strong><br>
                    <em>Claim:</em> Market research shows 73% want this feature<br>
                    <small>Source: TechReport 2024</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="evidence-card">
                    <strong>🥇 GOLD EVIDENCE</strong><br>
                    <em>Claim:</em> 3 competitors removed similar features after poor adoption<br>
                    <small>Source: Post-mortem Analysis</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.warning("⚡ **OBJECTION!** That market research was B2C focused, we're B2B!")
            
            elif i == 3:  # Cross-examination
                st.markdown("### 🎯 Critical Questions")
                st.info("**QA Engineer**: What about the 47 edge cases I've documented? Each one needs testing and maintenance.")
                st.info("**UX Designer**: Users are already confused by our current interface. This adds complexity without solving core pain points.")
        
        # Add delay for drama
        delay = 0.5 if intensity == "Quick" else 1.0 if intensity == "Standard" else 1.5
        time.sleep(delay)
    
    # Final verdict
    st.markdown("---")
    st.markdown("## 🏛️ Final Verdict")
    
    # Simulate judgment based on requirement
    confidence = random.randint(65, 95)
    
    # Simple heuristics for demo
    blockchain_keywords = ["blockchain", "crypto", "nft", "web3"]
    ai_keywords = ["ai", "machine learning", "artificial intelligence"]
    simple_keywords = ["search", "filter", "sort", "export"]
    
    req_lower = requirement.lower()
    
    if any(keyword in req_lower for keyword in blockchain_keywords):
        verdict = "REJECTED"
        confidence = random.randint(80, 95)
        alternative = "Use PostgreSQL with audit logs for immutable records"
        savings = 2100000
    elif any(keyword in req_lower for keyword in simple_keywords):
        verdict = "APPROVED"
        confidence = random.randint(75, 90)
        alternative = None
        savings = 0
    else:
        verdict = random.choice(["APPROVED", "REJECTED", "CONDITIONAL"])
        alternative = "Consider a simpler MVP approach first"
        savings = random.randint(500000, 3000000) if verdict == "REJECTED" else 0
    
    # Display verdict
    if verdict == "APPROVED":
        st.markdown(f"""
        <div class="verdict-approved">
        <h2 style="text-align: center;">✅ VERDICT: APPROVED ✅</h2>
        <h3 style="text-align: center;">Judge Confidence: {confidence}%</h3>
        <p><strong>Judge ({judge_type}):</strong> The evidence supports implementing this requirement. 
        Proceed with implementation while monitoring adoption closely.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="verdict-rejected">
        <h2 style="text-align: center;">❌ VERDICT: {verdict} ❌</h2>
        <h3 style="text-align: center;">Judge Confidence: {confidence}%</h3>
        <p><strong>Judge ({judge_type}):</strong> The evidence suggests significant risks and concerns. 
        The implementation complexity and maintenance burden outweigh potential benefits.</p>
        {f'<p><strong>Alternative:</strong> {alternative}</p>' if alternative else ''}
        {f'<h2 style="text-align: center;">💰 Money Saved: ${savings:,}</h2>' if savings > 0 else ''}
        </div>
        """, unsafe_allow_html=True)
    
    # Show confidence meters
    st.markdown("### 📊 Final Confidence Scores")
    col1, col2 = st.columns(2)
    
    with col1:
        pro_confidence = 100 - confidence if verdict == "REJECTED" else confidence
        st.metric("💚 PRO Team", f"{pro_confidence}%")
    
    with col2:
        con_confidence = confidence if verdict == "REJECTED" else 100 - confidence
        st.metric("❤️ CON Team", f"{con_confidence}%")
    
    # Celebrate or commiserate
    if verdict == "APPROVED":
        st.balloons()
    else:
        st.success("💡 **Money Saved!** Another bad requirement stopped before development.")

    # Add restart button
    if st.button("🔄 Analyze Another Requirement"):
        st.rerun()

if __name__ == "__main__":
    main()
#built with love
