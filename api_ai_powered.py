#!/usr/bin/env python3
"""
AI-Powered REST API for ReqDefender
Integrates with the real AI debate system from streamlit_simple.py
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="ReqDefender AI-Powered API",
    description="Real AI Agents Debate Your Requirements Using Claude/GPT",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import the AI-powered debate components
try:
    from research.searcher_working import WorkingResearchPipeline
    from arena.evidence_system import EvidenceGatherer, EvidenceScorer
    import anthropic
    import openai
    
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some components not available: {e}")
    COMPONENTS_AVAILABLE = False

# In-memory storage (in production, use a database)
debate_results = {}

class AIDebateEngine:
    """Core AI debate engine matching streamlit_simple.py functionality"""
    
    def __init__(self):
        self.setup_llm_clients()
        
    def setup_llm_clients(self):
        """Initialize LLM clients"""
        try:
            # Anthropic client
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key and "your_anthropic" not in anthropic_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
            else:
                self.anthropic_client = None
                
            # OpenAI client
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key and "your_openai" not in openai_key:
                self.openai_client = openai.OpenAI(api_key=openai_key)
            else:
                self.openai_client = None
                
        except Exception as e:
            print(f"LLM setup error: {e}")
            self.anthropic_client = None
            self.openai_client = None
    
    async def gather_real_evidence(self, requirement: str, max_sources: int = 10):
        """Gather evidence using real search"""
        if not COMPONENTS_AVAILABLE:
            return []
            
        try:
            pipeline = WorkingResearchPipeline()
            
            # Search for supporting evidence
            pro_results = await pipeline.search_evidence(requirement, "support")
            
            # Search for opposing evidence
            con_results = await pipeline.search_evidence(requirement, "oppose")
            
            # Create evidence objects
            gatherer = EvidenceGatherer()
            evidence_objects = await gatherer.gather_evidence(requirement, "neutral", max_sources=max_sources)
            
            return {
                "evidence_objects": evidence_objects,
                "pro_results": pro_results[:5],
                "con_results": con_results[:5],
                "total_sources": len(pro_results) + len(con_results)
            }
            
        except Exception as e:
            print(f"Evidence gathering error: {e}")
            return {"evidence_objects": [], "pro_results": [], "con_results": [], "total_sources": 0}
    
    async def generate_ai_arguments(self, requirement: str, evidence_objects: list, stance: str):
        """Generate AI arguments (PRO or CON)"""
        if not self.anthropic_client and not self.openai_client:
            # Fallback templates
            if stance == "PRO":
                return [
                    f"The evidence supports implementing {requirement} based on available sources.",
                    f"This requirement addresses documented needs and industry trends.",
                    f"Technical feasibility is demonstrated by similar implementations."
                ]
            else:
                return [
                    f"Implementation of {requirement} presents significant complexity risks.",
                    f"Resource allocation concerns may outweigh documented advantages.",
                    f"Alternative approaches could provide similar value with reduced risk."
                ]
        
        # Prepare evidence summary
        evidence_summary = "\n".join([
            f"- {str(e)[:200]}..." if len(str(e)) > 200 else f"- {str(e)}"
            for e in evidence_objects[:5]
        ])
        
        action = "argue FOR implementing" if stance == "PRO" else "argue AGAINST implementing"
        
        prompt = f"""You are a {stance} team agent in a requirements debate. Your job is to {action} this requirement.

REQUIREMENT: {requirement}

EVIDENCE AVAILABLE:
{evidence_summary}

Generate 3 strong, specific arguments {'supporting' if stance == 'PRO' else 'opposing'} this requirement. Each argument should:
- Reference the evidence provided
- Be concise but compelling
- Address practical {'benefits' if stance == 'PRO' else 'concerns and risks'}
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
            
            # Parse arguments
            arguments = [arg.strip().lstrip('-').strip() 
                        for arg in arguments_text.split('\n') 
                        if arg.strip() and not arg.strip().startswith('#')][:3]
            
            return arguments if arguments else [
                f"Standard argument {i+1} for {stance} stance on {requirement}"
                for i in range(3)
            ]
            
        except Exception as e:
            print(f"AI argument generation error: {e}")
            return [f"Argument {i+1} for {stance} stance (AI error)" for i in range(3)]
    
    async def generate_ai_verdict(self, requirement: str, pro_args: list, con_args: list, evidence_objects: list, judge_type: str = "Pragmatist"):
        """Generate AI-powered judge verdict"""
        if not self.anthropic_client and not self.openai_client:
            # Fallback logic
            pro_score = len(evidence_objects) * 10 + len(pro_args) * 5
            con_score = len(evidence_objects) * 8 + len(con_args) * 5
            
            if pro_score > con_score * 1.2:
                return {
                    "verdict": "APPROVED",
                    "confidence": 78.0,
                    "reasoning": f"Evidence and arguments support implementing {requirement}.",
                    "key_factors": "Technical feasibility, user value, implementation complexity",
                    "ai_powered": False
                }
            elif con_score > pro_score * 1.2:
                return {
                    "verdict": "REJECTED",
                    "confidence": 82.0,
                    "reasoning": f"Concerns outweigh benefits for {requirement} implementation.",
                    "key_factors": "Risk factors, resource requirements, complexity concerns",
                    "ai_powered": False
                }
            else:
                return {
                    "verdict": "NEEDS_RESEARCH",
                    "confidence": 65.0,
                    "reasoning": f"Mixed evidence for {requirement} requires further investigation.",
                    "key_factors": "Evidence quality, implementation scope, stakeholder alignment",
                    "ai_powered": False
                }
        
        # Prepare comprehensive prompt
        pro_summary = "\n".join([f"- {arg}" for arg in pro_args])
        con_summary = "\n".join([f"- {arg}" for arg in con_args])
        evidence_summary = "\n".join([
            f"- {str(e)[:150]}..." if len(str(e)) > 150 else f"- {str(e)}"
            for e in evidence_objects[:8]
        ])
        
        judge_personalities = {
            "Pragmatist": "You prioritize practical implementation concerns, cost-benefit analysis, and proven solutions. You're skeptical of unproven approaches.",
            "Innovator": "You favor cutting-edge solutions, creative approaches, and calculated risks for competitive advantage. You're optimistic about new technologies.",
            "User Advocate": "You prioritize user experience, accessibility, and features that directly benefit end users. You're cautious about complexity that doesn't serve users."
        }
        
        personality_context = judge_personalities.get(judge_type, judge_personalities["Pragmatist"])
        
        prompt = f"""You are an experienced software engineering judge with the personality of a {judge_type}. {personality_context}

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
            return self._parse_ai_judgment(judgment_text, requirement, evidence_objects, judge_type)
            
        except Exception as e:
            print(f"AI verdict generation error: {e}")
            return {
                "verdict": "NEEDS_RESEARCH",
                "confidence": 60.0,
                "reasoning": f"Analysis of {requirement} completed with limited AI capabilities.",
                "key_factors": "System limitations, fallback analysis",
                "ai_powered": False
            }
    
    def _parse_ai_judgment(self, judgment_text: str, requirement: str, evidence_objects: list, judge_type: str) -> dict:
        """Parse AI judge response"""
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
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning,
            "key_factors": key_factors,
            "evidence_count": len(evidence_objects),
            "judge_type": judge_type,
            "ai_powered": True
        }

# Global AI engine instance
ai_engine = AIDebateEngine() if COMPONENTS_AVAILABLE else None

# Request/Response Models
class AnalysisRequest(BaseModel):
    requirement: str = Field(..., description="The requirement to analyze")
    judge_type: str = Field("Pragmatist", description="Judge type: Pragmatist, Innovator, or User_Advocate")
    max_evidence: int = Field(10, description="Maximum evidence sources to gather")

class AnalysisResult(BaseModel):
    id: str
    requirement: str
    verdict: str
    confidence: float
    reasoning: str
    key_factors: str
    evidence_count: int
    pro_arguments: List[str]
    con_arguments: List[str]
    ai_powered: bool
    timestamp: datetime

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "ReqDefender AI-Powered API",
        "version": "2.0.0",
        "description": "Real AI Agents Debate Your Requirements Using Claude/GPT",
        "ai_status": {
            "components_available": COMPONENTS_AVAILABLE,
            "anthropic_ready": ai_engine.anthropic_client is not None if ai_engine else False,
            "openai_ready": ai_engine.openai_client is not None if ai_engine else False,
        },
        "endpoints": {
            "analyze": "/analyze",
            "quick": "/quick",
            "health": "/health",
            "stats": "/stats"
        }
    }

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_requirement(request: AnalysisRequest):
    """
    Analyze a requirement using real AI-powered debate
    
    This runs the complete flow:
    1. Gather real evidence from web searches
    2. Generate AI arguments (PRO vs CON)
    3. AI judge makes final verdict
    """
    if not ai_engine:
        raise HTTPException(status_code=503, detail="AI engine not available - missing dependencies")
    
    try:
        analysis_id = str(uuid.uuid4())
        
        # Step 1: Gather Evidence
        evidence_data = await ai_engine.gather_real_evidence(request.requirement, request.max_evidence)
        evidence_objects = evidence_data.get("evidence_objects", [])
        
        # Step 2: Generate Arguments
        pro_args = await ai_engine.generate_ai_arguments(request.requirement, evidence_objects, "PRO")
        con_args = await ai_engine.generate_ai_arguments(request.requirement, evidence_objects, "CON")
        
        # Step 3: AI Judge Verdict
        verdict_data = await ai_engine.generate_ai_verdict(
            request.requirement, pro_args, con_args, evidence_objects, request.judge_type
        )
        
        # Create result
        result = AnalysisResult(
            id=analysis_id,
            requirement=request.requirement,
            verdict=verdict_data["verdict"],
            confidence=verdict_data["confidence"],
            reasoning=verdict_data["reasoning"],
            key_factors=verdict_data["key_factors"],
            evidence_count=len(evidence_objects),
            pro_arguments=pro_args,
            con_arguments=con_args,
            ai_powered=verdict_data["ai_powered"],
            timestamp=datetime.now()
        )
        
        # Store result
        debate_results[analysis_id] = result.dict()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/quick")
async def quick_analysis(requirement: str):
    """Quick analysis with minimal evidence gathering"""
    try:
        result = await analyze_requirement(AnalysisRequest(
            requirement=requirement,
            judge_type="Pragmatist",
            max_evidence=5
        ))
        
        return {
            "requirement": requirement,
            "verdict": result.verdict,
            "confidence": result.confidence,
            "summary": f"{result.verdict} with {result.confidence:.1f}% confidence",
            "ai_powered": result.ai_powered,
            "evidence_sources": result.evidence_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")

@app.get("/result/{result_id}")
async def get_result(result_id: str):
    """Get detailed analysis result by ID"""
    if result_id not in debate_results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return debate_results[result_id]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components_available": COMPONENTS_AVAILABLE,
        "ai_engine_ready": ai_engine is not None,
        "stored_results": len(debate_results)
    }

@app.get("/stats")
async def get_stats():
    """Get API usage statistics"""
    if not debate_results:
        return {
            "total_analyses": 0,
            "verdicts": {},
            "ai_powered_percentage": 0,
            "average_confidence": 0
        }
    
    verdicts = {}
    ai_powered_count = 0
    total_confidence = 0
    
    for result in debate_results.values():
        verdict = result["verdict"]
        verdicts[verdict] = verdicts.get(verdict, 0) + 1
        total_confidence += result["confidence"]
        if result.get("ai_powered", False):
            ai_powered_count += 1
    
    return {
        "total_analyses": len(debate_results),
        "verdicts": verdicts,
        "ai_powered_percentage": (ai_powered_count / len(debate_results)) * 100 if debate_results else 0,
        "average_confidence": total_confidence / len(debate_results) if debate_results else 0,
        "recent_analyses": list(debate_results.values())[-3:]
    }

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting ReqDefender AI-Powered API")
    print(f"   Components Available: {COMPONENTS_AVAILABLE}")
    if ai_engine:
        print(f"   Anthropic Ready: {ai_engine.anthropic_client is not None}")
        print(f"   OpenAI Ready: {ai_engine.openai_client is not None}")
    print(f"   Server: http://localhost:8002")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
#built with love
