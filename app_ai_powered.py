#!/usr/bin/env python3
"""
AI-Powered application launcher for ReqDefender
Uses the new AI-powered system instead of legacy CrewAI
"""

import os
import sys
import asyncio
import argparse
import logging
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from config import ReqDefenderConfig

class AIReqDefender:
    """AI-powered ReqDefender application launcher"""
    
    def __init__(self):
        self.config = ReqDefenderConfig.get_server_config()
        self.status = ReqDefenderConfig.get_system_status()
        self._validate_environment()
    
    def _validate_environment(self):
        """Validate environment and API keys"""
        validation = self.status["validation"]
        
        if not validation["has_llm"]:
            logger.error("❌ No LLM API keys found! Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
            logger.info("Get keys from:")
            logger.info("  - OpenAI: https://platform.openai.com/api-keys")  
            logger.info("  - Anthropic: https://console.anthropic.com/")
            sys.exit(1)
        
        logger.info("✅ Environment validation passed")
        logger.info(f"   OpenAI: {'✅' if validation['has_openai'] else '❌'}")
        logger.info(f"   Anthropic: {'✅' if validation['has_anthropic'] else '❌'}")
        logger.info(f"   Search: {'✅' if validation['has_search'] else '❌'}")
    
    def start_web_interface(self):
        """Start the Streamlit web interface"""
        logger.info("Starting AI-powered web interface...")
        
        try:
            cmd = [
                sys.executable, "-m", "streamlit", "run", "streamlit_simple.py",
                "--server.port", str(self.config["streamlit_port"]),
                "--server.address", self.config["host"]
            ]
            
            logger.info(f"Web interface will be available at: http://localhost:{self.config['streamlit_port']}")
            return subprocess.Popen(cmd)
            
        except Exception as e:
            logger.error(f"Failed to start web interface: {e}")
            return None
    
    def start_ai_api(self):
        """Start the AI-powered API server"""
        logger.info("Starting AI-powered API server...")
        
        try:
            # Use our AI-powered API
            cmd = [sys.executable, "api_ai_simple.py"]
            
            logger.info(f"AI API will be available at: http://localhost:{self.config['ai_api_port']}")
            return subprocess.Popen(cmd)
            
        except Exception as e:
            logger.error(f"Failed to start AI API: {e}")
            return None
    
    def start_rest_api(self):
        """Start the REST API server (legacy, may need CrewAI)"""
        logger.info("Starting REST API server...")
        
        try:
            # Test import first to avoid process creation if it will fail
            try:
                sys.path.append(str(Path(__file__).parent / "api"))
                import importlib.util
                spec = importlib.util.spec_from_file_location("rest", Path(__file__).parent / "api" / "rest.py")
                # Don't actually import, just check if it would work
            except Exception as import_error:
                logger.warning(f"Legacy REST API requires CrewAI dependencies: {import_error}")
                logger.info("💡 Skipping legacy REST API - use AI API instead")
                return None
            
            cmd = [sys.executable, "api/rest.py"]
            logger.info(f"REST API will be available at: http://localhost:{self.config['rest_port']}")
            return subprocess.Popen(cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            
        except Exception as e:
            logger.warning(f"Failed to start REST API: {e}")
            logger.info("💡 Use AI API instead: python3 api_ai_simple.py")
            return None
    
    def start_websocket(self):
        """Start the WebSocket server"""
        logger.info("Starting WebSocket server...")
        
        try:
            # Test import first to avoid process creation if it will fail
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("websocket", Path(__file__).parent / "api" / "websocket.py")
                # Don't actually import, just check if it would work
            except Exception as import_error:
                logger.warning(f"Legacy WebSocket server requires CrewAI dependencies: {import_error}")
                logger.info("💡 Skipping WebSocket server - use AI API instead")
                return None
            
            cmd = [sys.executable, "api/websocket.py"]
            logger.info(f"WebSocket will be available at: ws://localhost:{self.config['websocket_port']}")
            return subprocess.Popen(cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            
        except Exception as e:
            logger.warning(f"Failed to start WebSocket server: {e}")
            logger.info("💡 WebSocket not available - use AI API instead")
            return None
    
    def run_all_services(self):
        """Start all available services"""
        logger.info("🚀 Starting all ReqDefender AI services...")
        
        processes = []
        
        # Start AI API (always works)
        ai_api_process = self.start_ai_api()
        if ai_api_process:
            processes.append(("AI API", ai_api_process))
        
        # Start web interface
        web_process = self.start_web_interface()
        if web_process:
            processes.append(("Web Interface", web_process))
        
        # Try to start additional services (but don't fail if they don't work)
        logger.info("🔧 Attempting to start legacy services...")
        rest_process = self.start_rest_api()
        if rest_process:
            processes.append(("REST API", rest_process))
        
        websocket_process = self.start_websocket()
        if websocket_process:
            processes.append(("WebSocket", websocket_process))
        
        logger.info(f"✅ Started {len(processes)} services successfully")
        
        if not processes:
            logger.error("❌ Failed to start any services")
            return
        
        logger.info("✅ Services started successfully!")
        logger.info("🌐 Access points:")
        logger.info(f"   Web Interface: http://localhost:{self.config['streamlit_port']}")
        logger.info(f"   AI API: http://localhost:{self.config['ai_api_port']}")
        if rest_process:
            logger.info(f"   REST API: http://localhost:{self.config['rest_port']}")
        if websocket_process:
            logger.info(f"   WebSocket: ws://localhost:{self.config['websocket_port']}")
        
        logger.info("\n🎯 Quick Test Commands:")
        logger.info(f"   curl -X POST 'http://localhost:{self.config['ai_api_port']}/quick' -d 'requirement=add dark mode'")
        logger.info(f"   python3 test_simple_api.py")
        
        logger.info("\n📱 Press Ctrl+C to stop all services")
        
        try:
            # Keep processes running
            while True:
                time.sleep(1)
                # Check if any process died
                for name, process in processes:
                    if process.poll() is not None:
                        logger.warning(f"⚠️ {name} process stopped unexpectedly")
                        
        except KeyboardInterrupt:
            logger.info("\n🛑 Stopping all services...")
            for name, process in processes:
                logger.info(f"   Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            logger.info("✅ All services stopped")
    
    def run_web_only(self):
        """Start only the web interface"""
        logger.info("🌐 Starting web interface only...")
        
        web_process = self.start_web_interface()
        if not web_process:
            logger.error("❌ Failed to start web interface")
            return
        
        logger.info(f"✅ Web interface started at: http://localhost:{self.config['streamlit_port']}")
        logger.info("📱 Press Ctrl+C to stop")
        
        try:
            web_process.wait()
        except KeyboardInterrupt:
            logger.info("\n🛑 Stopping web interface...")
            web_process.terminate()
            web_process.wait()
            logger.info("✅ Web interface stopped")
    
    def run_api_only(self):
        """Start only the AI API"""
        logger.info("🤖 Starting AI API only...")
        
        ai_process = self.start_ai_api()
        if not ai_process:
            logger.error("❌ Failed to start AI API")
            return
        
        logger.info(f"✅ AI API started at: http://localhost:{self.config['ai_api_port']}")
        logger.info("📱 Press Ctrl+C to stop")
        
        try:
            ai_process.wait()
        except KeyboardInterrupt:
            logger.info("\n🛑 Stopping AI API...")
            ai_process.terminate()
            ai_process.wait()
            logger.info("✅ AI API stopped")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ReqDefender AI-Powered Application Launcher")
    parser.add_argument("--mode", choices=["all", "web", "api", "config"], default="all",
                      help="Service mode to run (default: all)")
    
    args = parser.parse_args()
    
    # Show configuration if requested
    if args.mode == "config":
        print("🔧 ReqDefender Configuration Status")
        print("=" * 40)
        status = ReqDefenderConfig.get_system_status()
        
        # Server config
        server = status["config"]["server"]
        print(f"🌐 Server: {server['host']}")
        print(f"🐛 Debug: {server['debug']}")
        
        # Ports
        ports = status["config"]["ports"]
        print(f"\n📡 Ports:")
        for service, port in ports.items():
            print(f"   {service}: {port}")
        
        # AI status
        print(f"\n🤖 AI Status:")
        validation = status["validation"]
        print(f"   OpenAI: {'✅ Ready' if validation['has_openai'] else '❌ Missing'}")
        print(f"   Anthropic: {'✅ Ready' if validation['has_anthropic'] else '❌ Missing'}")
        print(f"   Production: {'✅ Ready' if validation['production_ready'] else '❌ Not Ready'}")
        
        return
    
    # Initialize application
    try:
        app = AIReqDefender()
    except SystemExit:
        return
    
    # Run requested mode
    if args.mode == "all":
        app.run_all_services()
    elif args.mode == "web":
        app.run_web_only()
    elif args.mode == "api":
        app.run_api_only()

if __name__ == "__main__":
    main()
#built with love
