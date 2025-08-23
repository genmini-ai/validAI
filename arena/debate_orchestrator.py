# arena/orchestrator.py
"""Main debate orchestration engine - manages the flow of the Agent Debate Arena"""

from crewai import Crew, Task, Process
from typing import Dict, List, Optional, AsyncGenerator, Tuple
from enum import Enum
from dataclasses import dataclass, field
import asyncio
import time
import json
from datetime import datetime
import random


class DebatePhase(Enum):
    """Phases of the debate"""
    PRE_BATTLE = "pre_battle"
    OPENING_STATEMENTS = "opening_statements"
    EVIDENCE_DUEL = "evidence_duel"
    CROSS_EXAMINATION = "cross_examination"
    FINAL_ARGUMENTS = "final_arguments"
    JUDGMENT = "judgment"
    COMPLETE = "complete"


class DebateEvent(Enum):
    """Types of events that occur during debate"""
    AGENT_SPEAKS = "agent_speaks"
    EVIDENCE_PRESENTED = "evidence_presented"
    OBJECTION_RAISED = "objection_raised"
    CONFIDENCE_UPDATE = "confidence_update"
    PHASE_CHANGE = "phase_change"
    VERDICT_RENDERED = "verdict_rendered"
    DRAMATIC_MOMENT = "dramatic_moment"


@dataclass
class DebateState:
    """Current state of the debate"""
    phase: DebatePhase = DebatePhase.PRE_BATTLE
    round_number: int = 0
    pro_confidence: float = 50.0
    con_confidence: float = 50.0
    pro_evidence_score: float = 0.0
    con_evidence_score: float = 0.0
    current_speaker: Optional[str] = None
    transcript: List[Dict] = field(default_factory=list)
    evidence_presented: List[Dict] = field(default_factory=list)
    objections: List[Dict] = field(default_factory=list)
    dramatic_moments: List[Dict] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    

@dataclass
class DebateEvent:
    """An event that occurs during the debate"""
    timestamp: datetime
    event_type: str
    agent: str
    content: Dict
    visual_effect: Optional[str] = None
    sound_effect: Optional[str] = None
    importance: int = 1  # 1-5, 5 being most important


class DebateOrchestrator:
    """Orchestrates the Agent Debate Arena"""
    
    def __init__(self,
                 pro_agents: List,
                 con_agents: List,
                 judge_agent,
                 debate_config: Optional[Dict] = None):
        """
        Initialize the debate orchestrator
        
        Args:
            pro_agents: List of agents arguing FOR the requirement
            con_agents: List of agents arguing AGAINST the requirement
            judge_agent: The judge who will render the verdict
            debate_config: Optional configuration for debate parameters
        """
        self.pro_agents = pro_agents
        self.con_agents = con_agents
        self.judge_agent = judge_agent
        self.state = DebateState()
        
        # Default configuration
        self.config = {
            "max_rounds": 4,
            "time_per_round": 45,  # seconds
            "evidence_weight_multiplier": 1.5,
            "objection_threshold": 0.7,  # Confidence threshold for objections
            "dramatic_moment_threshold": 20,  # Confidence swing for dramatic moment
            "enable_special_effects": True,
            "streaming_delay": 0.5  # Delay between events for dramatic effect
        }
        if debate_config:
            self.config.update(debate_config)
        
        self.event_queue: asyncio.Queue = asyncio.Queue()
        
    async def analyze_requirement(self, requirement: str) -> Dict:
        """
        Main entry point - analyze a requirement through debate
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            Complete analysis including verdict and debate transcript
        """
        # Initialize debate
        await self._initialize_debate(requirement)
        
        # Run debate phases
        await self._run_opening_statements(requirement)
        await self._run_evidence_duel(requirement)
        await self._run_cross_examination(requirement)
        await self._run_final_arguments(requirement)
        
        # Get judgment
        verdict = await self._run_judgment(requirement)
        
        # Compile results
        return self._compile_results(verdict)
    
    async def analyze_requirement_streaming(self, 
                                           requirement: str) -> AsyncGenerator[Dict, None]:
        """
        Analyze requirement with streaming events for real-time UI
        
        Yields:
            Stream of debate events for real-time display
        """
        # Start background debate task
        debate_task = asyncio.create_task(self.analyze_requirement(requirement))
        
        # Stream events while debate is running
        while self.state.phase != DebatePhase.COMPLETE:
            try:
                event = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=1.0
                )
                yield event
            except asyncio.TimeoutError:
                continue
        
        # Wait for debate to complete and yield final result
        result = await debate_task
        yield {
            "type": "final_result",
            "data": result
        }
    
    async def _initialize_debate(self, requirement: str):
        """Initialize the debate with requirement analysis"""
        self.state.phase = DebatePhase.PRE_BATTLE
        
        await self._emit_event(
            event_type="phase_change",
            agent="system",
            content={
                "phase": "pre_battle",
                "message": f"Analyzing requirement: {requirement}",
                "action": "Agents preparing arguments..."
            },
            visual_effect="fade_in"
        )
        
        # Simulate preparation time
        await asyncio.sleep(self.config["streaming_delay"] * 2)
        
        # Select primary speakers for each team
        self.primary_pro = random.choice(self.pro_agents)
        self.primary_con = random.choice(self.con_agents)
        
        await self._emit_event(
            event_type="agent_selection",
            agent="system",
            content={
                "pro_speaker": self.primary_pro.role,
                "con_speaker": self.primary_con.role,
                "message": "Champions selected for battle!"
            },
            visual_effect="spotlight",
            importance=3
        )
    
    async def _run_opening_statements(self, requirement: str):
        """Run the opening statements phase"""
        self.state.phase = DebatePhase.OPENING_STATEMENTS
        self.state.round_number = 1
        
        await self._emit_event(
            event_type="phase_change",
            agent="system",
            content={
                "phase": "opening_statements",
                "round": 1,
                "message": "ROUND 1: Opening Statements"
            },
            visual_effect="banner_slide",
            sound_effect="bell_ring"
        )
        
        # PRO team opening
        pro_opening = await self._get_agent_argument(
            self.primary_pro,
            f"Make a compelling opening statement for why we should implement: {requirement}"
        )
        
        await self._emit_event(
            event_type="agent_speaks",
            agent=self.primary_pro.role,
            content={
                "team": "PRO",
                "argument": pro_opening,
                "confidence_impact": 5
            },
            visual_effect="slide_left"
        )
        
        self.state.pro_confidence += 5
        await self._update_confidence()
        
        # CON team opening
        con_opening = await self._get_agent_argument(
            self.primary_con,
            f"Make a compelling opening statement for why we should NOT implement: {requirement}"
        )
        
        await self._emit_event(
            event_type="agent_speaks",
            agent=self.primary_con.role,
            content={
                "team": "CON",
                "argument": con_opening,
                "confidence_impact": 5
            },
            visual_effect="slide_right"
        )
        
        self.state.con_confidence += 5
        await self._update_confidence()
    
    async def _run_evidence_duel(self, requirement: str):
        """Run the evidence duel phase - rapid fire evidence exchange"""
        self.state.phase = DebatePhase.EVIDENCE_DUEL
        self.state.round_number = 2
        
        await self._emit_event(
            event_type="phase_change",
            agent="system",
            content={
                "phase": "evidence_duel",
                "round": 2,
                "message": "ROUND 2: Evidence Duel!"
            },
            visual_effect="lightning_flash",
            sound_effect="thunder",
            importance=4
        )
        
        # Simulate rapid evidence exchange
        evidence_rounds = 3
        for i in range(evidence_rounds):
            # PRO presents evidence
            pro_evidence = await self._gather_evidence(
                self.primary_pro,
                requirement,
                "support"
            )
            
            await self._present_evidence(
                agent=self.primary_pro,
                evidence=pro_evidence,
                team="PRO"
            )
            
            # Check for objection opportunity
            if pro_evidence["tier"] >= 3:  # Weak evidence
                await self._attempt_objection(
                    objecting_agent=self.primary_con,
                    evidence=pro_evidence,
                    team="CON"
                )
            
            # CON presents evidence
            con_evidence = await self._gather_evidence(
                self.primary_con,
                requirement,
                "oppose"
            )
            
            await self._present_evidence(
                agent=self.primary_con,
                evidence=con_evidence,
                team="CON"
            )
            
            # Check for objection opportunity
            if con_evidence["tier"] >= 3:
                await self._attempt_objection(
                    objecting_agent=self.primary_pro,
                    evidence=con_evidence,
                    team="PRO"
                )
            
            # Check for dramatic moment
            await self._check_dramatic_moment()
    
    async def _run_cross_examination(self, requirement: str):
        """Run the cross-examination phase"""
        self.state.phase = DebatePhase.CROSS_EXAMINATION
        self.state.round_number = 3
        
        await self._emit_event(
            event_type="phase_change",
            agent="system",
            content={
                "phase": "cross_examination",
                "round": 3,
                "message": "ROUND 3: Cross-Examination!"
            },
            visual_effect="split_screen",
            importance=3
        )
        
        # PRO questions CON
        pro_question = await self._generate_critical_question(
            self.primary_pro,
            requirement,
            "challenge_opposition"
        )
        
        await self._emit_event(
            event_type="critical_question",
            agent=self.primary_pro.role,
            content={
                "question": pro_question,
                "target": self.primary_con.role
            },
            visual_effect="zoom_in"
        )
        
        con_response = await self._respond_to_question(
            self.primary_con,
            pro_question
        )
        
        await self._emit_event(
            event_type="question_response",
            agent=self.primary_con.role,
            content={
                "response": con_response,
                "effectiveness": self._evaluate_response(con_response)
            }
        )
        
        # CON questions PRO
        con_question = await self._generate_critical_question(
            self.primary_con,
            requirement,
            "expose_weakness"
        )
        
        await self._emit_event(
            event_type="critical_question",
            agent=self.primary_con.role,
            content={
                "question": con_question,
                "target": self.primary_pro.role
            },
            visual_effect="zoom_in"
        )
        
        pro_response = await self._respond_to_question(
            self.primary_pro,
            con_question
        )
        
        await self._emit_event(
            event_type="question_response",
            agent=self.primary_pro.role,
            content={
                "response": pro_response,
                "effectiveness": self._evaluate_response(pro_response)
            }
        )
    
    async def _run_final_arguments(self, requirement: str):
        """Run the final arguments phase"""
        self.state.phase = DebatePhase.FINAL_ARGUMENTS
        self.state.round_number = 4
        
        await self._emit_event(
            event_type="phase_change",
            agent="system",
            content={
                "phase": "final_arguments",
                "round": 4,
                "message": "ROUND 4: Final Arguments!"
            },
            visual_effect="dramatic_pause",
            importance=4
        )
        
        # Check if this is a knockout situation
        if self.state.pro_confidence < 10:
            await self._knockout_finish("CON", self.primary_con)
        elif self.state.con_confidence < 10:
            await self._knockout_finish("PRO", self.primary_pro)
        else:
            # Normal final arguments
            await self._normal_final_arguments(requirement)
    
    async def _run_judgment(self, requirement: str) -> Dict:
        """Run the judgment phase"""
        self.state.phase = DebatePhase.JUDGMENT
        
        await self._emit_event(
            event_type="phase_change",
            agent="system",
            content={
                "phase": "judgment",
                "message": "The Judge deliberates..."
            },
            visual_effect="gavel_raise",
            sound_effect="drum_roll",
            importance=5
        )
        
        # Simulate deliberation
        await asyncio.sleep(self.config["streaming_delay"] * 3)
        
        # Judge reviews evidence and arguments
        verdict = await self._get_judge_verdict(requirement)
        
        await self._emit_event(
            event_type="verdict_rendered",
            agent=self.judge_agent.role,
            content={
                "verdict": verdict["decision"],
                "confidence": verdict["confidence"],
                "reasoning": verdict["reasoning"],
                "alternative": verdict.get("alternative"),
                "savings": verdict.get("savings")
            },
            visual_effect="gavel_strike" if verdict["decision"] == "REJECTED" else "confetti",
            sound_effect="gavel" if verdict["decision"] == "REJECTED" else "applause",
            importance=5
        )
        
        self.state.phase = DebatePhase.COMPLETE
        return verdict
    
    async def _emit_event(self, **kwargs):
        """Emit an event to the event queue"""
        event = DebateEvent(
            timestamp=datetime.now(),
            **kwargs
        )
        
        await self.event_queue.put(event.__dict__)
        
        # Add streaming delay for dramatic effect
        if self.config["enable_special_effects"]:
            await asyncio.sleep(self.config["streaming_delay"])
    
    async def _update_confidence(self):
        """Update and emit confidence changes"""
        await self._emit_event(
            event_type="confidence_update",
            agent="system",
            content={
                "pro_confidence": self.state.pro_confidence,
                "con_confidence": self.state.con_confidence
            },
            visual_effect="meter_change"
        )
    
    async def _check_dramatic_moment(self):
        """Check if a dramatic moment has occurred"""
        confidence_diff = abs(self.state.pro_confidence - self.state.con_confidence)
        
        if confidence_diff > self.config["dramatic_moment_threshold"]:
            leading_team = "PRO" if self.state.pro_confidence > self.state.con_confidence else "CON"
            
            await self._emit_event(
                event_type="dramatic_moment",
                agent="system",
                content={
                    "type": "momentum_shift",
                    "leading_team": leading_team,
                    "confidence_gap": confidence_diff,
                    "message": f"{leading_team} team takes commanding lead!"
                },
                visual_effect="screen_shake",
                sound_effect="crowd_gasp",
                importance=4
            )
            
            self.state.dramatic_moments.append({
                "round": self.state.round_number,
                "type": "momentum_shift",
                "details": f"{leading_team} dominance"
            })
    
    async def _attempt_objection(self, objecting_agent, evidence: Dict, team: str):
        """Attempt an objection to weak evidence"""
        if random.random() > self.config["objection_threshold"]:
            return
        
        objection = await self._generate_objection(objecting_agent, evidence)
        
        await self._emit_event(
            event_type="objection_raised",
            agent=objecting_agent.role,
            content={
                "objection": "OBJECTION!",
                "reason": objection,
                "target_evidence": evidence,
                "team": team
            },
            visual_effect="objection_splash",
            sound_effect="objection_shout",
            importance=4
        )
        
        # Reduce opposing team confidence
        if team == "PRO":
            self.state.con_confidence -= 10
        else:
            self.state.pro_confidence -= 10
        
        await self._update_confidence()
    
    async def _knockout_finish(self, winning_team: str, winning_agent):
        """Handle a knockout finish when one side's confidence is too low"""
        await self._emit_event(
            event_type="dramatic_moment",
            agent="system",
            content={
                "type": "knockout",
                "winning_team": winning_team,
                "message": "KNOCKOUT! Devastating victory!"
            },
            visual_effect="knockout_animation",
            sound_effect="knockout_bell",
            importance=5
        )
        
        # Winning agent delivers finishing move
        finishing_argument = await self._get_agent_argument(
            winning_agent,
            "Deliver your finishing argument - you've completely dominated this debate!"
        )
        
        await self._emit_event(
            event_type="finishing_move",
            agent=winning_agent.role,
            content={
                "argument": finishing_argument,
                "team": winning_team
            },
            visual_effect="epic_finish",
            sound_effect="victory_fanfare",
            importance=5
        )
    
    async def _normal_final_arguments(self, requirement: str):
        """Handle normal final arguments when neither side has knockout"""
        # Both sides make final appeals
        for agent, team in [(self.primary_pro, "PRO"), (self.primary_con, "CON")]:
            final_arg = await self._get_agent_argument(
                agent,
                f"Make your final, most compelling argument about {requirement}"
            )
            
            await self._emit_event(
                event_type="final_argument",
                agent=agent.role,
                content={
                    "argument": final_arg,
                    "team": team
                },
                visual_effect="spotlight_focus"
            )
    
    # Helper methods (simplified for brevity)
    async def _get_agent_argument(self, agent, prompt: str) -> str:
        """Get an argument from an agent"""
        # In real implementation, this would use the agent's LLM
        return f"{agent.role}'s argument about: {prompt}"
    
    async def _gather_evidence(self, agent, requirement: str, stance: str) -> Dict:
        """Gather evidence from research tools"""
        # Simplified - would actually use research tools
        return {
            "source": "Research Database",
            "claim": f"Evidence {'supporting' if stance == 'support' else 'opposing'} {requirement}",
            "tier": random.randint(1, 4),
            "relevance": random.random(),
            "url": "https://example.com/evidence"
        }
    
    async def _present_evidence(self, agent, evidence: Dict, team: str):
        """Present evidence in the debate"""
        impact = (5 - evidence["tier"]) * 5  # Higher tier = more impact
        
        await self._emit_event(
            event_type="evidence_presented",
            agent=agent.role,
            content={
                "evidence": evidence,
                "team": team,
                "impact": impact
            },
            visual_effect=f"evidence_tier_{evidence['tier']}",
            importance=min(5, 6 - evidence["tier"])
        )
        
        # Update confidence based on evidence
        if team == "PRO":
            self.state.pro_confidence += impact
            self.state.pro_evidence_score += impact
        else:
            self.state.con_confidence += impact
            self.state.con_evidence_score += impact
        
        await self._update_confidence()
    
    async def _generate_critical_question(self, agent, requirement: str, strategy: str) -> str:
        """Generate a critical question for cross-examination"""
        return f"Critical question from {agent.role} about {requirement}"
    
    async def _respond_to_question(self, agent, question: str) -> str:
        """Generate response to a critical question"""
        return f"{agent.role}'s response to: {question}"
    
    async def _generate_objection(self, agent, evidence: Dict) -> str:
        """Generate an objection to evidence"""
        return f"This evidence is flawed because..."
    
    def _evaluate_response(self, response: str) -> str:
        """Evaluate effectiveness of a response"""
        return random.choice(["strong", "moderate", "weak", "evasive"])
    
    async def _get_judge_verdict(self, requirement: str) -> Dict:
        """Get the judge's verdict"""
        # Simplified - would actually use judge agent
        return {
            "decision": "REJECTED" if self.state.con_confidence > self.state.pro_confidence else "APPROVED",
            "confidence": abs(self.state.con_confidence - self.state.pro_confidence),
            "reasoning": "Based on the evidence presented...",
            "alternative": "Consider this alternative approach...",
            "savings": 2100000 if self.state.con_confidence > self.state.pro_confidence else 0
        }
    
    def _compile_results(self, verdict: Dict) -> Dict:
        """Compile complete debate results"""
        return {
            "requirement": "The analyzed requirement",
            "verdict": verdict,
            "debate_summary": {
                "duration": (datetime.now() - self.state.start_time).seconds,
                "rounds": self.state.round_number,
                "final_confidence": {
                    "pro": self.state.pro_confidence,
                    "con": self.state.con_confidence
                },
                "evidence_scores": {
                    "pro": self.state.pro_evidence_score,
                    "con": self.state.con_evidence_score
                },
                "dramatic_moments": self.state.dramatic_moments,
                "objections": len(self.state.objections)
            },
            "transcript": self.state.transcript,
            "evidence": self.state.evidence_presented,
            "replay_available": True
        }
#built with love
