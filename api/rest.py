# api/rest.py
"""REST API for ReqDefender"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import uuid
import asyncio

# Add parent directory to path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from arena.debate_orchestrator import DebateOrchestrator
from agents.pro_team_agents import create_pro_team, get_pro_team_metadata
from agents.con_team_agents import create_con_team, get_con_team_metadata
from agents.judge_agent import create_judge, get_judge_metadata
from arena.evidence_system import EvidenceGatherer

# FastAPI app
app = FastAPI(
    title="ReqDefender REST API",
    description="AI Agents Debate Your Requirements to Death",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for debate results (in production, use a database)
debate_results = {}


class RequirementAnalysisRequest(BaseModel):
    """Request model for requirement analysis"""
    requirement: str = Field(..., description="The requirement to analyze")
    judge_type: str = Field("pragmatist", description="Type of judge: pragmatist, innovator, or user_advocate")
    debate_mode: str = Field("standard", description="Debate mode: quick, standard, or deep")
    
    class Config:
        schema_extra = {
            "example": {
                "requirement": "Add blockchain to our todo app",
                "judge_type": "pragmatist",
                "debate_mode": "standard"
            }
        }


class QuickAnalysisRequest(BaseModel):
    """Request model for quick analysis"""
    requirement: str = Field(..., description="The requirement to analyze")
    
    class Config:
        schema_extra = {
            "example": {
                "requirement": "Implement AI-powered code review"
            }
        }


class BatchAnalysisRequest(BaseModel):
    """Request model for batch analysis"""
    requirements: List[str] = Field(..., description="List of requirements to analyze")
    judge_type: str = Field("pragmatist", description="Judge type for all analyses")
    
    class Config:
        schema_extra = {
            "example": {
                "requirements": [
                    "Add blockchain to our app",
                    "Implement metaverse shopping",
                    "Build AI chatbot"
                ],
                "judge_type": "pragmatist"
            }
        }


class AnalysisResult(BaseModel):
    """Response model for analysis result"""
    id: str
    requirement: str
    verdict: str
    confidence: float
    key_evidence: List[Dict]
    alternative_suggestion: Optional[str]
    estimated_savings: Optional[float]
    debate_transcript: Optional[List[Dict]]
    timestamp: datetime


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "ReqDefender REST API",
        "version": "1.0.0",
        "description": "AI Agents Debate Your Requirements to Death",
        "endpoints": {
            "analyze": "/api/analyze",
            "quick_analyze": "/api/quick",
            "batch_analyze": "/api/batch",
            "result": "/api/result/{result_id}",
            "metadata": "/api/metadata",
            "search_evidence": "/api/evidence/search"
        }
    }


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_requirement(
    request: RequirementAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze a requirement through full agent debate
    
    This endpoint runs a complete debate with all phases and returns
    a comprehensive analysis including verdict, evidence, and transcript.
    """
    try:
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Create agents
        pro_team = create_pro_team()
        con_team = create_con_team()
        judge = create_judge(request.judge_type)
        
        # Configure debate based on mode
        debate_config = {
            "quick": {"max_rounds": 2, "streaming_delay": 0.3},
            "standard": {"max_rounds": 4, "streaming_delay": 0.5},
            "deep": {"max_rounds": 6, "streaming_delay": 0.7}
        }
        
        config = debate_config.get(request.debate_mode, debate_config["standard"])
        config["enable_special_effects"] = False  # Disable for API
        
        # Create orchestrator
        orchestrator = DebateOrchestrator(
            pro_agents=pro_team,
            con_agents=con_team,
            judge_agent=judge,
            debate_config=config
        )
        
        # Run analysis
        result = await orchestrator.analyze_requirement(request.requirement)
        
        # Create response
        analysis_result = AnalysisResult(
            id=analysis_id,
            requirement=request.requirement,
            verdict=result["verdict"]["decision"],
            confidence=result["verdict"]["confidence"],
            key_evidence=result.get("evidence", [])[:5],  # Top 5 evidence
            alternative_suggestion=result["verdict"].get("alternative_suggestion"),
            estimated_savings=result["verdict"].get("estimated_savings"),
            debate_transcript=result.get("transcript", []),
            timestamp=datetime.now()
        )
        
        # Store result
        debate_results[analysis_id] = analysis_result.dict()
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/quick")
async def quick_analyze(request: QuickAnalysisRequest):
    """
    Quick analysis with minimal debate rounds
    
    Provides a fast verdict with key points, suitable for rapid screening.
    """
    try:
        # Use quick configuration
        full_request = RequirementAnalysisRequest(
            requirement=request.requirement,
            judge_type="pragmatist",
            debate_mode="quick"
        )
        
        # Run analysis with quick settings
        result = await analyze_requirement(full_request, BackgroundTasks())
        
        # Return simplified result
        return {
            "requirement": result.requirement,
            "verdict": result.verdict,
            "confidence": result.confidence,
            "quick_summary": f"Verdict: {result.verdict} with {result.confidence:.1f}% confidence",
            "alternative": result.alternative_suggestion
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")


@app.post("/api/batch")
async def batch_analyze(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze multiple requirements in batch
    
    Useful for analyzing a backlog of requirements or comparing alternatives.
    """
    batch_id = str(uuid.uuid4())
    results = []
    
    for requirement in request.requirements:
        try:
            # Create analysis request
            analysis_request = RequirementAnalysisRequest(
                requirement=requirement,
                judge_type=request.judge_type,
                debate_mode="quick"  # Use quick mode for batch
            )
            
            # Run analysis
            result = await analyze_requirement(analysis_request, background_tasks)
            results.append({
                "requirement": requirement,
                "verdict": result.verdict,
                "confidence": result.confidence,
                "alternative": result.alternative_suggestion
            })
            
        except Exception as e:
            results.append({
                "requirement": requirement,
                "verdict": "ERROR",
                "confidence": 0,
                "error": str(e)
            })
    
    return {
        "batch_id": batch_id,
        "total_requirements": len(request.requirements),
        "results": results,
        "summary": {
            "approved": len([r for r in results if r["verdict"] == "APPROVED"]),
            "rejected": len([r for r in results if r["verdict"] == "REJECTED"]),
            "conditional": len([r for r in results if r["verdict"] == "CONDITIONAL"]),
            "needs_research": len([r for r in results if r["verdict"] == "NEEDS_RESEARCH"]),
            "errors": len([r for r in results if r.get("verdict") == "ERROR"])
        }
    }


@app.get("/api/result/{result_id}")
async def get_result(result_id: str):
    """
    Retrieve a specific analysis result by ID
    """
    if result_id not in debate_results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return debate_results[result_id]


@app.get("/api/metadata")
async def get_metadata():
    """
    Get metadata about agents and judges
    
    Returns information about available agents, judges, and their characteristics.
    """
    return {
        "pro_team": get_pro_team_metadata(),
        "con_team": get_con_team_metadata(),
        "judges": get_judge_metadata(),
        "debate_modes": {
            "quick": "2 rounds, fast analysis",
            "standard": "4 rounds, balanced analysis",
            "deep": "6 rounds, comprehensive analysis"
        }
    }


@app.post("/api/evidence/search")
async def search_evidence(
    query: str,
    stance: str = "neutral",
    max_results: int = 10
):
    """
    Search for evidence about a requirement
    
    Useful for pre-debate research or validating specific claims.
    """
    try:
        gatherer = EvidenceGatherer()
        evidence = await gatherer.gather_evidence(
            requirement=query,
            stance=stance,
            max_sources=max_results
        )
        
        # Convert evidence objects to dictionaries
        evidence_list = []
        for e in evidence:
            evidence_list.append({
                "claim": e.claim,
                "source": e.source,
                "url": e.url,
                "tier": e.tier.value,
                "score": e.total_score,
                "relevance": e.relevance_score,
                "credibility": e.credibility_score,
                "extracted_data": e.extracted_data
            })
        
        return {
            "query": query,
            "stance": stance,
            "total_found": len(evidence_list),
            "evidence": evidence_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evidence search failed: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "stored_results": len(debate_results)
    }


@app.get("/api/stats")
async def get_stats():
    """Get API usage statistics"""
    if not debate_results:
        return {
            "total_analyses": 0,
            "verdicts": {},
            "average_confidence": 0
        }
    
    verdicts = {}
    total_confidence = 0
    
    for result in debate_results.values():
        verdict = result["verdict"]
        verdicts[verdict] = verdicts.get(verdict, 0) + 1
        total_confidence += result["confidence"]
    
    return {
        "total_analyses": len(debate_results),
        "verdicts": verdicts,
        "average_confidence": total_confidence / len(debate_results) if debate_results else 0,
        "recent_analyses": list(debate_results.values())[-5:]  # Last 5
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
#built with love
