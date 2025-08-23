# api/websocket.py
"""WebSocket API for real-time debate streaming"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional
from datetime import datetime
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent directory to path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from arena.debate_orchestrator import DebateOrchestrator
from agents.pro_team_agents import create_pro_team
from agents.con_team_agents import create_con_team
from agents.judge_agent import create_judge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="ReqDefender WebSocket API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DebateRequest(BaseModel):
    """Request model for starting a debate"""
    requirement: str
    judge_type: str = "pragmatist"
    intensity: str = "standard"
    max_rounds: int = 4
    enable_effects: bool = True


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.debate_sessions: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and register a new connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        """Remove a disconnected client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.debate_sessions:
            del self.debate_sessions[client_id]
        logger.info(f"Client {client_id} disconnected")
    
    async def send_personal_message(self, message: Dict, client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)
    
    async def broadcast(self, message: Dict, room_id: Optional[str] = None):
        """Broadcast a message to all clients or specific room"""
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            # If room_id specified, only send to clients in that room
            if room_id and self.debate_sessions.get(client_id, {}).get("room_id") != room_id:
                continue
            
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)


# Connection manager instance
manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Main WebSocket endpoint for debate streaming"""
    await manager.connect(websocket, client_id)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "message": "Welcome to ReqDefender Agent Debate Arena!"
        }, client_id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "start_debate":
                await handle_start_debate(client_id, data)
            
            elif message_type == "stop_debate":
                await handle_stop_debate(client_id)
            
            elif message_type == "get_status":
                await handle_get_status(client_id)
            
            elif message_type == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }, client_id)
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected normally")
    
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)


async def handle_start_debate(client_id: str, data: Dict):
    """Handle starting a new debate"""
    try:
        # Extract parameters
        requirement = data.get("requirement")
        if not requirement:
            await manager.send_personal_message({
                "type": "error",
                "message": "Requirement is required"
            }, client_id)
            return
        
        config = {
            "judge_type": data.get("judge_type", "pragmatist"),
            "intensity": data.get("intensity", "standard"),
            "max_rounds": data.get("max_rounds", 4),
            "enable_effects": data.get("enable_effects", True)
        }
        
        # Create debate session
        session_id = str(uuid.uuid4())
        manager.debate_sessions[client_id] = {
            "session_id": session_id,
            "requirement": requirement,
            "config": config,
            "status": "starting",
            "start_time": datetime.now()
        }
        
        # Send debate starting message
        await manager.send_personal_message({
            "type": "debate_starting",
            "session_id": session_id,
            "requirement": requirement,
            "config": config
        }, client_id)
        
        # Start debate in background task
        asyncio.create_task(run_debate_session(client_id, session_id, requirement, config))
        
    except Exception as e:
        logger.error(f"Error starting debate: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Failed to start debate: {str(e)}"
        }, client_id)


async def run_debate_session(client_id: str, session_id: str, requirement: str, config: Dict):
    """Run a debate session and stream events to client"""
    try:
        # Update session status
        if client_id in manager.debate_sessions:
            manager.debate_sessions[client_id]["status"] = "running"
        
        # Create agents
        pro_team = create_pro_team()
        con_team = create_con_team()
        judge = create_judge(config["judge_type"])
        
        # Configure debate
        debate_config = {
            "max_rounds": config["max_rounds"],
            "enable_special_effects": config["enable_effects"],
            "streaming_delay": 0.5 if config["intensity"] == "quick" else 1.0
        }
        
        # Create orchestrator
        orchestrator = DebateOrchestrator(
            pro_agents=pro_team,
            con_agents=con_team,
            judge_agent=judge,
            debate_config=debate_config
        )
        
        # Stream debate events
        async for event in orchestrator.analyze_requirement_streaming(requirement):
            # Check if client still connected
            if client_id not in manager.active_connections:
                logger.info(f"Client {client_id} disconnected, stopping debate")
                break
            
            # Send event to client
            await manager.send_personal_message({
                "type": "debate_event",
                "session_id": session_id,
                "event": event
            }, client_id)
            
            # Check for final result
            if event.get("type") == "final_result":
                # Update session status
                if client_id in manager.debate_sessions:
                    manager.debate_sessions[client_id]["status"] = "completed"
                    manager.debate_sessions[client_id]["result"] = event.get("data")
                
                # Send completion message
                await manager.send_personal_message({
                    "type": "debate_completed",
                    "session_id": session_id,
                    "result": event.get("data")
                }, client_id)
                break
        
    except Exception as e:
        logger.error(f"Error in debate session: {e}")
        await manager.send_personal_message({
            "type": "debate_error",
            "session_id": session_id,
            "error": str(e)
        }, client_id)
        
        # Update session status
        if client_id in manager.debate_sessions:
            manager.debate_sessions[client_id]["status"] = "error"


async def handle_stop_debate(client_id: str):
    """Handle stopping a debate"""
    if client_id in manager.debate_sessions:
        session = manager.debate_sessions[client_id]
        session["status"] = "stopped"
        
        await manager.send_personal_message({
            "type": "debate_stopped",
            "session_id": session["session_id"]
        }, client_id)


async def handle_get_status(client_id: str):
    """Handle status request"""
    if client_id in manager.debate_sessions:
        session = manager.debate_sessions[client_id]
        await manager.send_personal_message({
            "type": "status",
            "session": session
        }, client_id)
    else:
        await manager.send_personal_message({
            "type": "status",
            "message": "No active debate session"
        }, client_id)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ReqDefender WebSocket API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "websocket": "/ws/{client_id}",
            "health": "/health",
            "stats": "/stats"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(manager.active_connections),
        "active_debates": len([s for s in manager.debate_sessions.values() if s["status"] == "running"])
    }


@app.get("/stats")
async def stats():
    """Statistics endpoint"""
    return {
        "total_connections": len(manager.active_connections),
        "total_sessions": len(manager.debate_sessions),
        "sessions_by_status": {
            status: len([s for s in manager.debate_sessions.values() if s["status"] == status])
            for status in ["starting", "running", "completed", "stopped", "error"]
        },
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
#built with love
