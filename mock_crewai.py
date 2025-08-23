# mock_crewai.py
"""Mock implementations for CrewAI since it's not available for Python 3.9"""

from typing import List, Dict, Optional, Any
import asyncio

class Agent:
    """Mock Agent class"""
    def __init__(self, role: str, goal: str, backstory: str, tools: List = None, 
                 llm=None, max_iter: int = 3, verbose: bool = True, 
                 allow_delegation: bool = False):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        self.llm = llm
        self.max_iter = max_iter
        self.verbose = verbose
        self.allow_delegation = allow_delegation
    
    def __str__(self):
        return f"Agent(role='{self.role}')"

class Task:
    """Mock Task class"""
    def __init__(self, description: str, agent: Agent, tools: List = None):
        self.description = description
        self.agent = agent
        self.tools = tools or []

class Crew:
    """Mock Crew class"""
    def __init__(self, agents: List[Agent], tasks: List[Task], 
                 process: str = "sequential", verbose: bool = True):
        self.agents = agents
        self.tasks = tasks
        self.process = process
        self.verbose = verbose
    
    async def kickoff(self) -> Dict:
        """Mock execution that returns a simple result"""
        return {
            "result": f"Mock crew execution with {len(self.agents)} agents and {len(self.tasks)} tasks",
            "agents": [agent.role for agent in self.agents]
        }

class Process:
    """Mock Process enum"""
    sequential = "sequential"
    hierarchical = "hierarchical"
#built with love
