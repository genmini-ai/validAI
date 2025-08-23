#!/usr/bin/env python3
"""
Simple standalone debate test without Streamlit dependencies
Tests the core LLM agent debate process
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from research.searcher_working import WorkingResearchPipeline
from config import ReqDefenderConfig

# Simple LLM client initialization
def get_llm_client():
    """Get available LLM client"""
    config = ReqDefenderConfig.get_system_status()
    
    if config["validation"]["has_anthropic"]:
        try:
            from anthropic import Anthropic
            return Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")), "anthropic"
        except Exception as e:
            print(f"Anthropic client failed: {e}")
    
    if config["validation"]["has_openai"]:
        try:
            from openai import OpenAI
            return OpenAI(api_key=os.getenv("OPENAI_API_KEY")), "openai"
        except Exception as e:
            print(f"OpenAI client failed: {e}")
    
    return None, None

async def generate_agent_argument(client, client_type, requirement, evidence, agent_role, stance):
    """Generate argument from an AI agent"""
    
    # Prepare evidence text
    evidence_text = "\n".join([
        f"- {e.get('content', str(e))[:150]}..." for e in evidence[:3]
    ])
    
    prompt = f"""You are a {agent_role} in a requirements debate. 

REQUIREMENT: {requirement}

EVIDENCE:
{evidence_text}

Your stance is {stance}. Generate a brief, compelling argument (2-3 sentences) based on the evidence.
Be specific and reference evidence where relevant."""

    try:
        if client_type == "anthropic":
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
            
        elif client_type == "openai":
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
            
    except Exception as e:
        print(f"   ❌ {agent_role} argument generation failed: {e}")
        return f"Template argument: {stance} position on {requirement} based on evidence analysis."

async def generate_judge_verdict(client, client_type, requirement, pro_args, con_args, evidence):
    """Generate AI judge verdict"""
    
    prompt = f"""You are a pragmatic judge evaluating a requirements debate.

REQUIREMENT: {requirement}

PRO ARGUMENTS:
{chr(10).join([f"• {arg}" for arg in pro_args])}

CON ARGUMENTS:
{chr(10).join([f"• {arg}" for arg in con_args])}

EVIDENCE: {len(evidence)} sources analyzed

Render a verdict: APPROVED, REJECTED, or NEEDS_RESEARCH
Provide confidence (0-100%) and 1-2 sentences reasoning.

Format: VERDICT|CONFIDENCE|REASONING"""

    try:
        if client_type == "anthropic":
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.content[0].text.strip()
            
        elif client_type == "openai":
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content.strip()
        
        # Parse result
        parts = result.split("|")
        if len(parts) >= 3:
            return {
                "verdict": parts[0].strip(),
                "confidence": float(parts[1].strip().replace("%", "")),
                "reasoning": parts[2].strip(),
                "ai_powered": True
            }
        
    except Exception as e:
        print(f"   ❌ Judge verdict generation failed: {e}")
    
    # Fallback
    return {
        "verdict": "NEEDS_RESEARCH",
        "confidence": 50.0,
        "reasoning": f"Template verdict for {requirement} based on available evidence.",
        "ai_powered": False
    }

async def run_simple_debate_test():
    """Run a simple debate test"""
    print("🎭 Simple LLM Agent Debate Test")
    print("=" * 40)
    
    # Test requirement
    requirement = "implement real-time chat feature in mobile app"
    print(f"🎯 Requirement: {requirement}")
    
    # Check LLM availability
    client, client_type = get_llm_client()
    if client:
        print(f"🤖 Using {client_type.upper()} for AI agents")
    else:
        print("⚠️ No LLM client available - using template responses")
    
    try:
        # Phase 1: Gather Evidence
        print(f"\n🔍 Phase 1: Gathering evidence...")
        pipeline = WorkingResearchPipeline()
        
        # Quick evidence search (limited to avoid rate limits)
        pro_evidence = await pipeline.search_evidence(requirement, "support")
        con_evidence = await pipeline.search_evidence(requirement, "oppose")
        
        all_evidence = pro_evidence[:2] + con_evidence[:2]  # Limit total
        print(f"   ✅ Evidence collected: {len(all_evidence)} sources")
        
        if not all_evidence:
            print("   ⚠️ No evidence found - using mock evidence")
            all_evidence = [
                {"content": f"Positive case study about {requirement}", "source": "TechReport"},
                {"content": f"Implementation challenges for {requirement}", "source": "DevBlog"}
            ]
        
        # Phase 2: Agent Arguments
        print(f"\n⚔️ Phase 2: Agent debate...")
        
        if client:
            print("   🤖 Generating AI agent arguments...")
            
            # PRO team arguments
            pro_args = []
            pro_agents = ["Product Manager", "UX Designer", "Sales Champion"]
            
            for agent in pro_agents[:2]:  # Limit to avoid rate limits
                arg = await generate_agent_argument(
                    client, client_type, requirement, all_evidence, agent, "PRO"
                )
                pro_args.append(arg)
                print(f"      💚 {agent}: {arg[:70]}...")
            
            # CON team arguments  
            con_args = []
            con_agents = ["Senior Architect", "QA Engineer", "Security Expert"]
            
            for agent in con_agents[:2]:  # Limit to avoid rate limits  
                arg = await generate_agent_argument(
                    client, client_type, requirement, all_evidence, agent, "CON"
                )
                con_args.append(arg)
                print(f"      ❤️ {agent}: {arg[:70]}...")
                
        else:
            # Template arguments
            pro_args = [
                f"Evidence supports implementing {requirement} for user engagement",
                f"Market research indicates strong demand for {requirement}"
            ]
            con_args = [
                f"Implementation complexity of {requirement} may exceed benefits", 
                f"Security concerns and resource constraints challenge {requirement}"
            ]
            print("   📝 Using template arguments (no LLM available)")
        
        # Phase 3: Judge Verdict
        print(f"\n⚖️ Phase 3: Judge verdict...")
        
        if client:
            verdict = await generate_judge_verdict(
                client, client_type, requirement, pro_args, con_args, all_evidence
            )
            print(f"   🏛️ AI Judge Verdict: {verdict['verdict']}")
            print(f"   📊 Confidence: {verdict['confidence']:.1f}%")
            print(f"   🤔 Reasoning: {verdict['reasoning']}")
            
        else:
            verdict = {
                "verdict": "NEEDS_RESEARCH",
                "confidence": 50.0,
                "reasoning": f"Template verdict for {requirement}",
                "ai_powered": False
            }
            print(f"   📝 Template verdict: {verdict['verdict']} ({verdict['confidence']}%)")
        
        # Phase 4: Results Summary
        print(f"\n🎉 Debate Results:")
        print(f"   ✅ Evidence sources: {len(all_evidence)}")
        print(f"   ✅ PRO arguments: {len(pro_args)}")
        print(f"   ✅ CON arguments: {len(con_args)}")
        print(f"   ✅ Final verdict: {verdict['verdict']}")
        print(f"   🤖 AI-powered: {'Yes' if client else 'No (templates used)'}")
        
        print(f"\n🚀 Simple debate test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Debate test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_simple_debate_test())
    sys.exit(0 if success else 1)
#built with love
