#!/usr/bin/env python3
"""
Multi-Round Debate API for ReqDefender
Real agents debate across multiple rounds with rebuttals and responses
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum
import uuid
import sys
import os
from pathlib import Path
import asyncio

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="ReqDefender Multi-Round Debate API",
    description="Real AI Agents Engage in Multi-Round Debates with Rebuttals",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import AI and search components
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

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Debate Round Types
class RoundType(str, Enum):
    OPENING = "opening"
    REBUTTAL = "rebuttal"
    COUNTER_REBUTTAL = "counter_rebuttal"
    CLOSING = "closing"

class DebateRound(BaseModel):
    """Single round of debate"""
    round_number: int
    round_type: RoundType
    pro_arguments: List[str]
    con_arguments: List[str]
    pro_references_con: List[str]  # Which CON points PRO addressed
    con_references_pro: List[str]  # Which PRO points CON addressed
    timestamp: datetime

class DebateTranscript(BaseModel):
    """Complete debate record"""
    requirement: str
    rounds: List[DebateRound]
    evidence: List[str]
    final_summaries: Dict[str, str]  # PRO and CON final summaries
    judge_verdict: Dict
    total_rounds: int
    debate_duration_seconds: float

class MultiRoundDebateEngine:
    """Orchestrates multi-round debates between AI agents"""
    
    def __init__(self):
        self.setup_llm_clients()
        self.debate_memory = {}  # Track arguments across rounds
        
    def setup_llm_clients(self):
        """Initialize LLM clients"""
        self.anthropic_client = None
        self.openai_client = None
        
        if ANTHROPIC_AVAILABLE:
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key and "your_" not in anthropic_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                
        if OPENAI_AVAILABLE:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key and "your_" not in openai_key:
                self.openai_client = openai.OpenAI(api_key=openai_key)
    
    async def gather_evidence(self, requirement: str) -> List[str]:
        """Gather evidence for the debate"""
        if not SEARCH_AVAILABLE:
            return [
                f"Market research shows demand for {requirement}",
                f"Technical feasibility analysis indicates implementation challenges",
                f"User feedback suggests mixed reception for similar features",
                f"Cost-benefit analysis reveals resource implications"
            ]
        
        try:
            pipeline = WorkingResearchPipeline()
            pro_results = await pipeline.search_evidence(requirement, "support")
            con_results = await pipeline.search_evidence(requirement, "oppose")
            
            evidence = []
            for result in pro_results[:3]:
                snippet = result.get('snippet', '')[:200]
                evidence.append(f"PRO Evidence: {snippet}")
            
            for result in con_results[:3]:
                snippet = result.get('snippet', '')[:200]
                evidence.append(f"CON Evidence: {snippet}")
                
            return evidence if evidence else [f"Limited evidence available for {requirement}"]
            
        except Exception as e:
            return [f"Evidence gathering failed: {str(e)[:100]}"]
    
    async def generate_opening_arguments(self, requirement: str, evidence: List[str], stance: str) -> List[str]:
        """Generate opening arguments for first round"""
        if not self.anthropic_client and not self.openai_client:
            return [f"{stance} opening argument 1", f"{stance} opening argument 2", f"{stance} opening argument 3"]
        
        evidence_text = "\n".join(evidence[:4])
        
        prompt = f"""You are the {stance} team in a formal debate about a software requirement.

REQUIREMENT: {requirement}

EVIDENCE AVAILABLE:
{evidence_text}

Generate 3 strong OPENING arguments {'supporting' if stance == 'PRO' else 'opposing'} this requirement.
Each argument should:
- Present a unique perspective
- Be specific and evidence-based
- Be 50-75 words
- Sound professional and compelling

Format as numbered list (1. 2. 3.)"""

        try:
            if self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=800,
                    messages=[{"role": "user", "content": prompt}]
                )
                text = response.content[0].text
            elif self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=800,
                    messages=[{"role": "user", "content": prompt}]
                )
                text = response.choices[0].message.content
            else:
                return [f"{stance} argument {i+1}" for i in range(3)]
            
            # Parse arguments
            arguments = []
            for line in text.split('\n'):
                line = line.strip()
                if line and line[0].isdigit():
                    arg = line.lstrip('0123456789. ').strip()
                    if len(arg) > 20:
                        arguments.append(arg)
            
            return arguments[:3] if arguments else [f"{stance} opening {i+1}" for i in range(3)]
            
        except Exception as e:
            return [f"{stance} argument (error: {str(e)[:30]})"]
    
    async def generate_rebuttal(self, requirement: str, stance: str, 
                                own_previous: List[str], opponent_arguments: List[str],
                                round_number: int) -> Tuple[List[str], List[str]]:
        """Generate rebuttal arguments that respond to opponent"""
        if not self.anthropic_client and not self.openai_client:
            return ([f"{stance} rebuttal {i+1}" for i in range(3)], 
                   [f"Responds to opponent point {i+1}" for i in range(2)])
        
        opponent_text = "\n".join([f"{i+1}. {arg}" for i, arg in enumerate(opponent_arguments)])
        own_text = "\n".join([f"- {arg}" for arg in own_previous])
        
        prompt = f"""You are the {stance} team in round {round_number} of a debate.

REQUIREMENT: {requirement}

OPPONENT'S ARGUMENTS:
{opponent_text}

YOUR PREVIOUS ARGUMENTS:
{own_text}

Generate 3 REBUTTAL arguments that:
1. DIRECTLY ADDRESS and counter specific opponent points (cite which ones)
2. Strengthen your {stance} position with new evidence or logic
3. Expose weaknesses in opponent's reasoning

Format:
ARGUMENT 1: [your rebuttal]
RESPONDS TO: [which opponent point(s) this addresses]

ARGUMENT 2: [your rebuttal]
RESPONDS TO: [which opponent point(s) this addresses]

ARGUMENT 3: [your rebuttal]
RESPONDS TO: [which opponent point(s) this addresses]"""

        try:
            if self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                text = response.content[0].text
            elif self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                text = response.choices[0].message.content
            else:
                return ([f"{stance} rebuttal {i+1}" for i in range(3)], ["Point 1", "Point 2"])
            
            # Parse rebuttals and references
            arguments = []
            references = []
            
            lines = text.split('\n')
            current_arg = ""
            current_ref = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith("ARGUMENT"):
                    if current_arg:
                        arguments.append(current_arg)
                    current_arg = line.split(':', 1)[1].strip() if ':' in line else ""
                elif line.startswith("RESPONDS TO:"):
                    current_ref = line.split(':', 1)[1].strip() if ':' in line else ""
                    if current_ref:
                        references.append(current_ref)
                elif line and current_arg and not line.startswith("ARGUMENT"):
                    current_arg += " " + line
            
            if current_arg:
                arguments.append(current_arg)
            
            return (arguments[:3] if arguments else [f"{stance} rebuttal {i+1}" for i in range(3)],
                   references[:3] if references else ["Opponent's main points"])
            
        except Exception as e:
            return ([f"{stance} rebuttal error: {str(e)[:30]}"], ["Error parsing"])
    
    async def generate_closing_summary(self, requirement: str, stance: str,
                                      all_rounds: List[DebateRound]) -> str:
        """Generate final closing summary for judge"""
        if not self.anthropic_client and not self.openai_client:
            return f"{stance} team closing: We have demonstrated our position through evidence and reasoning."
        
        # Compile all arguments from this side
        all_arguments = []
        for round in all_rounds:
            if stance == "PRO":
                all_arguments.extend(round.pro_arguments)
            else:
                all_arguments.extend(round.con_arguments)
        
        arguments_text = "\n".join([f"- {arg[:100]}..." for arg in all_arguments[:6]])
        
        prompt = f"""You are the {stance} team making your FINAL CLOSING STATEMENT to the judge.

REQUIREMENT: {requirement}

YOUR KEY ARGUMENTS ACROSS ALL ROUNDS:
{arguments_text}

Write a powerful 100-150 word closing statement that:
1. Synthesizes your strongest points
2. Highlights critical flaws in opponent's case
3. Makes a compelling final appeal to the judge
4. Emphasizes why your position should prevail

Be persuasive, concise, and memorable."""

        try:
            if self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
            elif self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content.strip()
            else:
                return f"{stance} closing: Our arguments demonstrate clear merit."
                
        except Exception as e:
            return f"{stance} closing summary (error: {str(e)[:50]})"
    
    async def judge_debate(self, requirement: str, rounds: List[DebateRound],
                          pro_summary: str, con_summary: str, evidence: List[str]) -> Dict:
        """Judge makes final verdict after all rounds"""
        if not self.anthropic_client and not self.openai_client:
            return {
                "verdict": "NEEDS_RESEARCH",
                "confidence": 70.0,
                "reasoning": "Automated verdict based on debate analysis",
                "winning_arguments": ["Key point 1", "Key point 2"],
                "losing_weaknesses": ["Weakness 1"],
                "decisive_factors": "Evidence quality and argument coherence"
            }
        
        # Compile debate highlights
        debate_summary = "DEBATE PROGRESSION:\n"
        for i, round in enumerate(rounds):
            debate_summary += f"\nROUND {i+1} ({round.round_type}):\n"
            debate_summary += f"PRO: {round.pro_arguments[0][:100]}...\n" if round.pro_arguments else ""
            debate_summary += f"CON: {round.con_arguments[0][:100]}...\n" if round.con_arguments else ""
        
        evidence_text = "\n".join([f"- {e[:100]}..." for e in evidence[:5]])
        
        prompt = f"""You are an impartial JUDGE evaluating a formal debate.

REQUIREMENT: {requirement}

{debate_summary}

PRO TEAM CLOSING:
{pro_summary}

CON TEAM CLOSING:
{con_summary}

EVIDENCE:
{evidence_text}

Deliver your verdict:

VERDICT: [APPROVED/REJECTED/NEEDS_RESEARCH]
CONFIDENCE: [0-100]%
REASONING: [2-3 sentences on why this side won]
WINNING_ARGUMENTS: [2-3 strongest points from winning side]
LOSING_WEAKNESSES: [1-2 critical flaws in losing side]
DECISIVE_FACTORS: [What tipped the scales]"""

        try:
            if self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=800,
                    messages=[{"role": "user", "content": prompt}]
                )
                text = response.content[0].text
            elif self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=800,
                    messages=[{"role": "user", "content": prompt}]
                )
                text = response.choices[0].message.content
            else:
                return {"verdict": "NEEDS_RESEARCH", "confidence": 65.0}
            
            # Parse judge response
            result = {
                "verdict": "NEEDS_RESEARCH",
                "confidence": 75.0,
                "reasoning": "",
                "winning_arguments": [],
                "losing_weaknesses": [],
                "decisive_factors": ""
            }
            
            lines = text.split('\n')
            current_field = None
            
            for line in lines:
                line = line.strip()
                if line.startswith("VERDICT:"):
                    v = line.replace("VERDICT:", "").strip().upper()
                    if "APPROVED" in v:
                        result["verdict"] = "APPROVED"
                    elif "REJECTED" in v:
                        result["verdict"] = "REJECTED"
                elif line.startswith("CONFIDENCE:"):
                    try:
                        c = line.replace("CONFIDENCE:", "").strip().replace("%", "")
                        result["confidence"] = float(c)
                    except:
                        pass
                elif line.startswith("REASONING:"):
                    current_field = "reasoning"
                    reasoning_text = line.replace("REASONING:", "").strip()
                    if reasoning_text:
                        result["reasoning"] = reasoning_text
                elif line.startswith("WINNING_ARGUMENTS:"):
                    current_field = "winning"
                    args = line.replace("WINNING_ARGUMENTS:", "").strip()
                    if args:
                        result["winning_arguments"].append(args)
                elif line.startswith("LOSING_WEAKNESSES:"):
                    current_field = "losing"
                    weak = line.replace("LOSING_WEAKNESSES:", "").strip()
                    if weak:
                        result["losing_weaknesses"].append(weak)
                elif line.startswith("DECISIVE_FACTORS:"):
                    result["decisive_factors"] = line.replace("DECISIVE_FACTORS:", "").strip()
                elif line and current_field == "reasoning" and not line.startswith(("WINNING_", "LOSING_", "DECISIVE_")):
                    # Continue collecting reasoning text
                    if result["reasoning"]:
                        result["reasoning"] += " " + line
                    else:
                        result["reasoning"] = line
                elif line and current_field == "winning" and line.startswith("-"):
                    result["winning_arguments"].append(line.lstrip("- "))
                elif line and current_field == "losing" and line.startswith("-"):
                    result["losing_weaknesses"].append(line.lstrip("- "))
            
            return result
            
        except Exception as e:
            return {
                "verdict": "ERROR",
                "confidence": 0.0,
                "reasoning": f"Judge error: {str(e)[:100]}",
                "winning_arguments": [],
                "losing_weaknesses": [],
                "decisive_factors": "System error"
            }
    
    async def run_debate(self, requirement: str, num_rounds: int = 3) -> DebateTranscript:
        """Run complete multi-round debate"""
        start_time = datetime.now()
        rounds = []
        
        # Step 1: Gather evidence
        evidence = await self.gather_evidence(requirement)
        
        # Step 2: Opening arguments
        pro_args = await self.generate_opening_arguments(requirement, evidence, "PRO")
        con_args = await self.generate_opening_arguments(requirement, evidence, "CON")
        
        rounds.append(DebateRound(
            round_number=1,
            round_type=RoundType.OPENING,
            pro_arguments=pro_args,
            con_arguments=con_args,
            pro_references_con=[],
            con_references_pro=[],
            timestamp=datetime.now()
        ))
        
        # Step 3: Rebuttal rounds
        for round_num in range(2, min(num_rounds + 1, 5)):  # Max 4 rounds total
            # PRO rebuts CON's previous arguments
            pro_rebuttals, pro_refs = await self.generate_rebuttal(
                requirement, "PRO", pro_args, con_args, round_num
            )
            
            # CON rebuts PRO's previous arguments
            con_rebuttals, con_refs = await self.generate_rebuttal(
                requirement, "CON", con_args, pro_args, round_num
            )
            
            round_type = RoundType.REBUTTAL if round_num == 2 else RoundType.COUNTER_REBUTTAL
            
            rounds.append(DebateRound(
                round_number=round_num,
                round_type=round_type,
                pro_arguments=pro_rebuttals,
                con_arguments=con_rebuttals,
                pro_references_con=pro_refs,
                con_references_pro=con_refs,
                timestamp=datetime.now()
            ))
            
            # Update arguments for next round
            pro_args = pro_rebuttals
            con_args = con_rebuttals
        
        # Step 4: Closing summaries
        pro_summary = await self.generate_closing_summary(requirement, "PRO", rounds)
        con_summary = await self.generate_closing_summary(requirement, "CON", rounds)
        
        # Step 5: Judge verdict
        verdict = await self.judge_debate(requirement, rounds, pro_summary, con_summary, evidence)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        return DebateTranscript(
            requirement=requirement,
            rounds=rounds,
            evidence=evidence,
            final_summaries={"PRO": pro_summary, "CON": con_summary},
            judge_verdict=verdict,
            total_rounds=len(rounds),
            debate_duration_seconds=duration
        )

# Initialize debate engine
debate_engine = MultiRoundDebateEngine()

# Request Models
class DebateRequest(BaseModel):
    requirement: str = Field(..., description="Requirement to debate")
    num_rounds: int = Field(3, description="Number of debate rounds (2-4)")

# API Endpoints
@app.get("/")
async def root():
    """API information"""
    return {
        "service": "ReqDefender Multi-Round Debate API",
        "version": "3.0.0",
        "features": [
            "Multi-round debates with rebuttals",
            "Agents respond to each other's arguments",
            "Closing summaries before final verdict",
            "Detailed debate transcripts"
        ],
        "ai_status": {
            "anthropic_ready": debate_engine.anthropic_client is not None,
            "openai_ready": debate_engine.openai_client is not None,
        },
        "endpoints": ["/debate", "/quick-debate", "/health"]
    }

@app.post("/debate")
async def run_full_debate(request: DebateRequest):
    """Run complete multi-round debate"""
    try:
        # Validate rounds
        num_rounds = max(2, min(request.num_rounds, 4))
        
        # Run debate
        transcript = await debate_engine.run_debate(request.requirement, num_rounds)
        
        return {
            "success": True,
            "requirement": request.requirement,
            "verdict": transcript.judge_verdict["verdict"],
            "confidence": transcript.judge_verdict["confidence"],
            "total_rounds": transcript.total_rounds,
            "duration_seconds": transcript.debate_duration_seconds,
            "transcript": transcript.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debate failed: {str(e)}")

@app.post("/quick-debate")
async def quick_debate(requirement: str):
    """Run quick 2-round debate"""
    try:
        transcript = await debate_engine.run_debate(requirement, num_rounds=2)
        
        return {
            "requirement": requirement,
            "verdict": transcript.judge_verdict["verdict"],
            "confidence": transcript.judge_verdict["confidence"],
            "summary": transcript.judge_verdict["reasoning"],
            "pro_closing": transcript.final_summaries["PRO"][:200] + "...",
            "con_closing": transcript.final_summaries["CON"][:200] + "...",
            "rounds_completed": transcript.total_rounds,
            "duration": f"{transcript.debate_duration_seconds:.1f}s"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick debate failed: {str(e)}")

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "ai_available": debate_engine.anthropic_client is not None or debate_engine.openai_client is not None,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    from config import ReqDefenderConfig
    
    config = ReqDefenderConfig.get_uvicorn_config("debate_api")
    
    print("🎭 Starting Multi-Round Debate API")
    print(f"   Anthropic: {'✓' if debate_engine.anthropic_client else '✗'}")
    print(f"   OpenAI: {'✓' if debate_engine.openai_client else '✗'}")
    print(f"   Server: http://{config['host']}:{config['port']}")
    
    uvicorn.run(app, **config)

#built with love
#built with love
