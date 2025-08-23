#!/usr/bin/env python3
"""Simplified REST API for ReqDefender"""

from fastapi import FastAPI
from pydantic import BaseModel
import random
from datetime import datetime

app = FastAPI(
    title="ReqDefender REST API",
    description="AI Agents Debate Your Requirements to Death",
    version="1.0.0"
)

class AnalysisRequest(BaseModel):
    requirement: str
    judge_type: str = "pragmatist"
    intensity: str = "standard"

class AnalysisResult(BaseModel):
    requirement: str
    verdict: str
    confidence: float
    reasoning: str
    alternative: str = None
    estimated_savings: float = None
    timestamp: datetime

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ReqDefender API",
        "version": "1.0.0",
        "description": "AI Agents Debate Your Requirements to Death",
        "status": "running",
        "endpoints": {
            "analyze": "/analyze",
            "quick": "/quick",
            "health": "/health"
        }
    }

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_requirement(request: AnalysisRequest):
    """Analyze a requirement through simulated agent debate"""
    
    # Simple mock analysis logic
    req_lower = request.requirement.lower()
    
    # Heuristic-based analysis for demo
    if any(word in req_lower for word in ["blockchain", "crypto", "nft", "web3"]):
        verdict = "REJECTED"
        confidence = random.uniform(80, 95)
        reasoning = "Blockchain adds unnecessary complexity and maintenance burden. Historical data shows poor adoption rates."
        alternative = "Use PostgreSQL with audit logs for immutable records"
        savings = 2100000.0
        
    elif any(word in req_lower for word in ["search", "filter", "sort", "export"]):
        verdict = "APPROVED"
        confidence = random.uniform(75, 90)
        reasoning = "This is a practical feature with clear user value and straightforward implementation."
        alternative = None
        savings = None
        
    elif any(word in req_lower for word in ["ai", "machine learning", "artificial intelligence"]):
        verdict = "CONDITIONAL"
        confidence = random.uniform(60, 75)
        reasoning = "AI features can provide value but require careful scoping and user research to avoid over-engineering."
        alternative = "Start with rule-based approach, then add ML if data supports it"
        savings = None
        
    else:
        verdict = random.choice(["APPROVED", "REJECTED", "CONDITIONAL", "NEEDS_RESEARCH"])
        confidence = random.uniform(60, 85)
        reasoning = "Mixed evidence from agent debate. Some concerns about complexity vs. user value."
        alternative = "Consider a simpler MVP approach first"
        savings = random.uniform(500000, 2000000) if verdict == "REJECTED" else None
    
    return AnalysisResult(
        requirement=request.requirement,
        verdict=verdict,
        confidence=round(confidence, 1),
        reasoning=reasoning,
        alternative=alternative,
        estimated_savings=savings,
        timestamp=datetime.now()
    )

@app.post("/quick")
async def quick_analysis(requirement: str):
    """Quick analysis with minimal processing"""
    result = await analyze_requirement(AnalysisRequest(
        requirement=requirement,
        judge_type="pragmatist",
        intensity="quick"
    ))
    
    return {
        "requirement": requirement,
        "verdict": result.verdict,
        "confidence": result.confidence,
        "summary": f"{result.verdict} with {result.confidence}% confidence"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ReqDefender API"
    }

@app.get("/stats")
async def get_stats():
    """Get API statistics"""
    return {
        "message": "ReqDefender API is running",
        "agents": {
            "pro_team": ["Product Visionary", "Sales Champion", "UX Designer"],
            "con_team": ["Senior Architect", "QA Engineer", "Data Analyst"],
            "judges": ["Pragmatist", "Innovator", "User Advocate"]
        },
        "sample_requirements": [
            "Add blockchain to our todo app",
            "Implement search functionality", 
            "Build AI-powered recommendations"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
#built with love
