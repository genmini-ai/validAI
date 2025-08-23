#!/usr/bin/env python3
"""
AI-Powered REST API for ReqDefender - Simplified version
Uses the same AI logic as streamlit_simple.py without heavy dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import uuid
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

# Try to import AI components
try:
    from research.searcher_working import WorkingResearchPipeline
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False
    print("Warning: Search components not available")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: Anthropic not available")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not available")

# In-memory storage
debate_results = {}

class SimpleAIDebateEngine:
    """Simplified AI debate engine"""
    
    def __init__(self):
        self.setup_llm_clients()
        
    def setup_llm_clients(self):
        """Initialize LLM clients"""
        try:
            # Anthropic client
            if ANTHROPIC_AVAILABLE:
                anthropic_key = os.getenv("ANTHROPIC_API_KEY")
                if anthropic_key and "your_anthropic" not in anthropic_key:
                    self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                else:
                    self.anthropic_client = None
            else:
                self.anthropic_client = None
                
            # OpenAI client
            if OPENAI_AVAILABLE:
                openai_key = os.getenv("OPENAI_API_KEY")
                if openai_key and "your_openai" not in openai_key:
                    self.openai_client = openai.OpenAI(api_key=openai_key)
                else:
                    self.openai_client = None
            else:
                self.openai_client = None
                
        except Exception as e:
            print(f"LLM setup error: {e}")
            self.anthropic_client = None
            self.openai_client = None
    
    async def gather_simple_evidence(self, requirement: str, max_sources: int = 5):
        """Gather evidence using real search when available"""
        if not SEARCH_AVAILABLE:
            # Return mock evidence only if search is not available
            return [
                f"Evidence 1: {requirement} is commonly requested in software projects",
                f"Evidence 2: Implementation involves user interface and backend changes",
                f"Evidence 3: Similar features have been successfully deployed in production",
                f"Evidence 4: User feedback suggests demand for this functionality",
                f"Evidence 5: Technical feasibility confirmed by development team"
            ]
        
        try:
            # Use real search pipeline
            pipeline = WorkingResearchPipeline()
            
            # Search for supporting and opposing evidence
            pro_results = await pipeline.search_evidence(requirement, "support")
            con_results = await pipeline.search_evidence(requirement, "oppose")
            
            # Extract evidence with PRO/CON labels for clarity
            evidence = []
            
            # Add PRO evidence (up to 3 sources)
            for result in pro_results[:3]:
                snippet = result.get('snippet', result.get('content', f'Supporting evidence for {requirement}'))
                evidence.append(f"PRO: {snippet[:150]}...")
            
            # Add CON evidence (up to 2 sources for balance)  
            for result in con_results[:2]:
                snippet = result.get('snippet', result.get('content', f'Concerns about {requirement}'))
                evidence.append(f"CON: {snippet[:150]}...")
                
            # Return real evidence if found, otherwise fallback
            return evidence if evidence else [
                f"Evidence found for {requirement} implementation",
                f"Mixed perspectives on technical and business impact"
            ]
            
        except Exception as e:
            # Fallback to basic evidence on any error
            return [f"Research indicates {requirement} requires careful evaluation"]
    
    async def generate_ai_arguments(self, requirement: str, evidence: list, stance: str):
        """Generate AI arguments"""
        if not self.anthropic_client and not self.openai_client:
            # Fallback templates
            if stance == "PRO":
                return [
                    f"Evidence supports implementing {requirement} based on user demand and technical feasibility",
                    f"Similar implementations have proven successful in production environments",
                    f"The feature addresses documented user needs and business requirements"
                ]
            else:
                return [
                    f"Implementation of {requirement} may introduce complexity and maintenance overhead",
                    f"Resource allocation should consider priority against other development work",
                    f"Alternative approaches might deliver similar value with reduced implementation cost"
                ]
        
        # Prepare evidence summary
        evidence_text = "\n".join([f"- {e}" for e in evidence[:4]])
        
        action = "argue FOR implementing" if stance == "PRO" else "argue AGAINST implementing"
        
        prompt = f"""You are a {stance} team agent in a software requirements debate. Your job is to {action} this requirement.

REQUIREMENT: {requirement}

EVIDENCE:
{evidence_text}

Generate 3 concise, professional arguments {'supporting' if stance == 'PRO' else 'opposing'} this requirement. Each should:
- Be specific and actionable
- Reference practical considerations
- Sound professional and technical
- Be under 100 words each

Format as a numbered list."""

        try:
            if self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=400,
                    messages=[{"role": "user", "content": prompt}]
                )
                arguments_text = response.content[0].text
            elif self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=400,
                    messages=[{"role": "user", "content": prompt}]
                )
                arguments_text = response.choices[0].message.content
            else:
                return [f"Template argument {i+1} for {stance} stance" for i in range(3)]
            
            # Parse arguments
            arguments = []
            lines = arguments_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Clean up the argument
                    clean_arg = line.lstrip('0123456789.-•').strip()
                    if clean_arg and len(clean_arg) > 20:
                        arguments.append(clean_arg)
                        if len(arguments) >= 3:
                            break
            
            return arguments if arguments else [
                f"AI generated argument 1 for {stance} stance on {requirement}",
                f"AI generated argument 2 for {stance} stance on {requirement}", 
                f"AI generated argument 3 for {stance} stance on {requirement}"
            ]
            
        except Exception as e:
            print(f"AI argument generation error: {e}")
            return [f"Argument {i+1} for {stance} stance (AI error: {str(e)[:50]})" for i in range(3)]
    
    async def generate_ai_verdict(self, requirement: str, pro_args: list, con_args: list, evidence: list, judge_type: str = "Pragmatist"):
        """Generate AI-powered judge verdict"""
        if not self.anthropic_client and not self.openai_client:
            # Simple fallback logic
            pro_score = len(evidence) * 5 + len(pro_args) * 3
            con_score = len(evidence) * 4 + len(con_args) * 3
            
            if pro_score > con_score * 1.3:
                return {
                    "verdict": "APPROVED",
                    "confidence": 78.0,
                    "reasoning": f"Analysis supports implementing {requirement} based on evidence and arguments.",
                    "key_factors": "User value, technical feasibility, business impact"
                }
            elif con_score > pro_score * 1.3:
                return {
                    "verdict": "REJECTED",
                    "confidence": 82.0,
                    "reasoning": f"Concerns outweigh benefits for {requirement} implementation.",
                    "key_factors": "Implementation complexity, resource constraints, risk factors"
                }
            else:
                return {
                    "verdict": "NEEDS_RESEARCH",
                    "confidence": 65.0,
                    "reasoning": f"Mixed evidence for {requirement} requires additional investigation.",
                    "key_factors": "Evidence quality, scope definition, stakeholder alignment"
                }
        
        # AI-powered analysis
        pro_summary = "\n".join([f"- {arg}" for arg in pro_args])
        con_summary = "\n".join([f"- {arg}" for arg in con_args])
        evidence_summary = "\n".join([f"- {e[:100]}..." for e in evidence[:5]])
        
        judge_personalities = {
            "Pragmatist": "practical implementation concerns and proven solutions",
            "Innovator": "cutting-edge approaches and competitive advantage", 
            "User_Advocate": "user experience and direct user benefits"
        }
        
        focus = judge_personalities.get(judge_type, judge_personalities["Pragmatist"])
        
        prompt = f"""You are a {judge_type} software engineering judge focused on {focus}.

REQUIREMENT: {requirement}

PRO ARGUMENTS:
{pro_summary}

CON ARGUMENTS:
{con_summary}

EVIDENCE:
{evidence_summary}

Make a verdict: APPROVED, REJECTED, or NEEDS_RESEARCH

Format your response as:
VERDICT: [choice]
CONFIDENCE: [0-100]%
REASONING: [2-3 sentences]
KEY_FACTORS: [main considerations]"""

        try:
            if self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=300,
                    messages=[{"role": "user", "content": prompt}]
                )
                judgment_text = response.content[0].text
            elif self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=300,
                    messages=[{"role": "user", "content": prompt}]
                )
                judgment_text = response.choices[0].message.content
            else:
                return {"verdict": "NEEDS_RESEARCH", "confidence": 60.0, "reasoning": "No AI available", "key_factors": "System limitations"}
            
            # Parse response
            verdict = "NEEDS_RESEARCH"
            confidence = 75.0
            reasoning = f"Analysis of {requirement} completed."
            key_factors = "Standard evaluation factors"
            
            lines = judgment_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("VERDICT:"):
                    v_text = line.replace("VERDICT:", "").strip()
                    if "APPROVED" in v_text.upper():
                        verdict = "APPROVED"
                    elif "REJECTED" in v_text.upper():
                        verdict = "REJECTED"
                    elif "NEEDS_RESEARCH" in v_text.upper():
                        verdict = "NEEDS_RESEARCH"
                elif line.startswith("CONFIDENCE:"):
                    try:
                        c_text = line.replace("CONFIDENCE:", "").strip().replace("%", "")
                        confidence = float(c_text)
                    except:
                        pass
                elif line.startswith("REASONING:"):
                    reasoning = line.replace("REASONING:", "").strip()
                elif line.startswith("KEY_FACTORS:"):
                    key_factors = line.replace("KEY_FACTORS:", "").strip()
            
            return {
                "verdict": verdict,
                "confidence": confidence,
                "reasoning": reasoning,
                "key_factors": key_factors
            }
            
        except Exception as e:
            print(f"AI verdict generation error: {e}")
            return {
                "verdict": "NEEDS_RESEARCH",
                "confidence": 60.0,
                "reasoning": f"Analysis completed with AI limitations: {str(e)[:50]}",
                "key_factors": "Technical analysis, system constraints"
            }

# Initialize AI engine
ai_engine = SimpleAIDebateEngine()

# Request/Response Models
class AnalysisRequest(BaseModel):
    requirement: str = Field(..., description="The requirement to analyze")
    judge_type: str = Field("Pragmatist", description="Judge type: Pragmatist, Innovator, or User_Advocate")
    max_evidence: int = Field(5, description="Maximum evidence sources")

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
    """API information"""
    return {
        "service": "ReqDefender AI-Powered API (Simplified)",
        "version": "2.0.0",
        "description": "Real AI Agents Debate Your Requirements",
        "ai_status": {
            "search_available": SEARCH_AVAILABLE,
            "anthropic_ready": ai_engine.anthropic_client is not None,
            "openai_ready": ai_engine.openai_client is not None,
        },
        "endpoints": ["/analyze", "/quick", "/health", "/stats"]
    }

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_requirement(request: AnalysisRequest):
    """Full AI-powered requirement analysis"""
    try:
        analysis_id = str(uuid.uuid4())
        
        # Step 1: Gather Evidence
        evidence = await ai_engine.gather_simple_evidence(request.requirement, request.max_evidence)
        
        # Step 2: Generate Arguments
        pro_args = await ai_engine.generate_ai_arguments(request.requirement, evidence, "PRO")
        con_args = await ai_engine.generate_ai_arguments(request.requirement, evidence, "CON")
        
        # Step 3: AI Verdict
        verdict_data = await ai_engine.generate_ai_verdict(
            request.requirement, pro_args, con_args, evidence, request.judge_type
        )
        
        # Create result
        result = AnalysisResult(
            id=analysis_id,
            requirement=request.requirement,
            verdict=verdict_data["verdict"],
            confidence=verdict_data["confidence"],
            reasoning=verdict_data["reasoning"],
            key_factors=verdict_data["key_factors"],
            evidence_count=len(evidence),
            pro_arguments=pro_args,
            con_arguments=con_args,
            ai_powered=(ai_engine.anthropic_client is not None or ai_engine.openai_client is not None),
            timestamp=datetime.now()
        )
        
        # Store result
        debate_results[analysis_id] = result.dict()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/quick")
async def quick_analysis(requirement: str):
    """Quick analysis"""
    try:
        result = await analyze_requirement(AnalysisRequest(
            requirement=requirement,
            judge_type="Pragmatist",
            max_evidence=3
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
    """Get analysis result by ID"""
    if result_id not in debate_results:
        raise HTTPException(status_code=404, detail="Result not found")
    return debate_results[result_id]

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ai_ready": ai_engine.anthropic_client is not None or ai_engine.openai_client is not None,
        "search_ready": SEARCH_AVAILABLE,
        "stored_results": len(debate_results)
    }

@app.get("/stats")
async def get_stats():
    """Usage statistics"""
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
        "ai_powered_percentage": (ai_powered_count / len(debate_results)) * 100,
        "average_confidence": total_confidence / len(debate_results),
        "recent_analyses": [
            {
                "requirement": r["requirement"][:50] + "..." if len(r["requirement"]) > 50 else r["requirement"],
                "verdict": r["verdict"],
                "confidence": r["confidence"]
            }
            for r in list(debate_results.values())[-3:]
        ]
    }

if __name__ == "__main__":
    import uvicorn
    from config import ReqDefenderConfig
    
    # Get server configuration
    config = ReqDefenderConfig.get_uvicorn_config("ai_api")
    
    print("🚀 Starting ReqDefender AI-Powered API (Simplified)")
    print(f"   Search Available: {SEARCH_AVAILABLE}")
    print(f"   Anthropic Ready: {ai_engine.anthropic_client is not None}")
    print(f"   OpenAI Ready: {ai_engine.openai_client is not None}")
    print(f"   Server: http://{config['host']}:{config['port']}")
    
    uvicorn.run(app, **config)
#built with love
