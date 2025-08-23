# app.py
"""Main application entry point for ReqDefender"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReqDefender:
    """Main ReqDefender application class"""
    
    def __init__(self):
        self.config = self._load_config()
        self._validate_environment()
    
    def _load_config(self) -> Dict:
        """Load application configuration"""
        return {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
            "brave_api_key": os.getenv("BRAVE_SEARCH_API_KEY"),
            "google_api_key": os.getenv("GOOGLE_API_KEY"),
            "google_cse_id": os.getenv("GOOGLE_CSE_ID"),
            "streamlit_port": int(os.getenv("STREAMLIT_PORT", 8501)),
            "websocket_port": int(os.getenv("WEBSOCKET_PORT", 8000)),
            "rest_port": int(os.getenv("REST_PORT", 8001)),
            "debug": os.getenv("DEBUG", "false").lower() == "true"
        }
    
    def _validate_environment(self):
        """Validate required environment variables"""
        required_vars = []
        
        # At least one LLM API key is required
        if not self.config["openai_api_key"] and not self.config["anthropic_api_key"]:
            required_vars.append("OPENAI_API_KEY or ANTHROPIC_API_KEY")
        
        # Search API (Brave is preferred, but not strictly required due to DuckDuckGo fallback)
        if not self.config["brave_api_key"]:
            logger.warning("BRAVE_SEARCH_API_KEY not set. Using DuckDuckGo as fallback (limited results)")
        
        if required_vars:
            logger.error(f"Missing required environment variables: {', '.join(required_vars)}")
            logger.info("Please set them in your .env file or environment")
            sys.exit(1)
    
    def analyze(self, 
                requirement: str,
                debate_mode: str = "standard",
                judge_personality: str = "pragmatist") -> Dict:
        """
        Analyze a requirement through agent debate
        
        Args:
            requirement: The requirement to analyze
            debate_mode: "quick", "standard", or "deep"
            judge_personality: "pragmatist", "innovator", or "user_advocate"
            
        Returns:
            Analysis result with verdict and details
        """
        from arena.debate_orchestrator import DebateOrchestrator
        from agents.pro_team_agents import create_pro_team
        from agents.con_team_agents import create_con_team
        from agents.judge_agent import create_judge
        
        logger.info(f"Analyzing requirement: {requirement}")
        
        # Create agents
        pro_team = create_pro_team()
        con_team = create_con_team()
        judge = create_judge(judge_personality)
        
        # Configure debate
        debate_configs = {
            "quick": {"max_rounds": 2, "streaming_delay": 0.3},
            "standard": {"max_rounds": 4, "streaming_delay": 0.5},
            "deep": {"max_rounds": 6, "streaming_delay": 0.7}
        }
        
        config = debate_configs.get(debate_mode, debate_configs["standard"])
        config["enable_special_effects"] = False
        
        # Create orchestrator
        orchestrator = DebateOrchestrator(
            pro_agents=pro_team,
            con_agents=con_team,
            judge_agent=judge,
            debate_config=config
        )
        
        # Run analysis
        result = asyncio.run(orchestrator.analyze_requirement(requirement))
        
        # Format result
        return {
            "requirement": requirement,
            "verdict": result["verdict"]["decision"],
            "confidence": result["verdict"]["confidence"],
            "reasoning": result["verdict"].get("reasoning"),
            "alternative": result["verdict"].get("alternative_suggestion"),
            "savings": result["verdict"].get("estimated_savings"),
            "key_evidence": result.get("evidence", [])[:5],
            "debate_summary": result.get("debate_summary")
        }
    
    def run_streamlit(self, interface="simple"):
        """Launch the Streamlit web interface"""
        logger.info(f"Starting Streamlit interface ({interface})...")
        import subprocess
        
        # Choose interface
        if interface == "debate":
            streamlit_script = Path(__file__).parent / "streamlit_debate.py"
        else:
            streamlit_script = Path(__file__).parent / "streamlit_simple.py"
        
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run",
                str(streamlit_script),
                "--server.port", str(self.config["streamlit_port"]),
                "--server.address", "0.0.0.0"
            ])
        except KeyboardInterrupt:
            logger.info("Streamlit interface stopped")
        except Exception as e:
            logger.error(f"Failed to start Streamlit: {e}")
            sys.exit(1)
    
    def run_websocket_server(self):
        """Launch the WebSocket API server"""
        logger.info("Starting WebSocket server...")
        import uvicorn
        from api.websocket import app
        
        try:
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=self.config["websocket_port"],
                log_level="info" if self.config["debug"] else "warning"
            )
        except KeyboardInterrupt:
            logger.info("WebSocket server stopped")
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            sys.exit(1)
    
    def run_rest_server(self):
        """Launch the REST API server"""
        logger.info("Starting REST API server...")
        import uvicorn
        from api.rest import app
        
        try:
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=self.config["rest_port"],
                log_level="info" if self.config["debug"] else "warning"
            )
        except KeyboardInterrupt:
            logger.info("REST API server stopped")
        except Exception as e:
            logger.error(f"Failed to start REST API server: {e}")
            sys.exit(1)
    
    def run_all_services(self, interface="simple"):
        """Run all services concurrently"""
        import concurrent.futures
        import signal
        
        logger.info("Starting all ReqDefender services...")
        
        def signal_handler(signum, frame):
            logger.info("Shutting down services...")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(self.run_streamlit, interface),
                executor.submit(self.run_websocket_server),
                executor.submit(self.run_rest_server),
                executor.submit(self.run_debate_api)
            ]
            
            # Wait for any service to complete (or fail)
            concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
    
    def run_debate_api(self):
        """Launch the multi-round debate API"""
        logger.info("Starting Multi-Round Debate API...")
        import subprocess
        
        try:
            subprocess.run([sys.executable, "api_debate.py"])
        except KeyboardInterrupt:
            logger.info("Debate API stopped")
        except Exception as e:
            logger.error(f"Failed to start Debate API: {e}")
            sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ReqDefender - AI Agents Debate Your Requirements to Death",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all services (web UI + APIs)
  python app.py
  
  # Run only the web interface
  python app.py --mode web
  
  # Run only the REST API
  python app.py --mode rest
  
  # Analyze a requirement from CLI
  python app.py analyze "Add blockchain to our todo app"
  
  # Quick analysis with specific judge
  python app.py quick "Implement AI chatbot" --judge innovator
  
  # Batch analysis from file
  python app.py batch requirements.txt --output results.csv
        """
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Default command (run all services)
    parser.add_argument(
        "--mode",
        choices=["all", "web", "rest", "websocket", "debate"],
        default="all",
        help="Which service(s) to run"
    )
    parser.add_argument(
        "--interface",
        choices=["simple", "debate"],
        default="simple",
        help="Which web interface to use"
    )
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a requirement")
    analyze_parser.add_argument("requirement", help="The requirement to analyze")
    analyze_parser.add_argument(
        "--mode",
        choices=["quick", "standard", "deep"],
        default="standard",
        help="Debate intensity"
    )
    analyze_parser.add_argument(
        "--judge",
        choices=["pragmatist", "innovator", "user_advocate"],
        default="pragmatist",
        help="Judge personality"
    )
    
    # Quick analysis command
    quick_parser = subparsers.add_parser("quick", help="Quick requirement analysis")
    quick_parser.add_argument("requirement", help="The requirement to analyze")
    quick_parser.add_argument(
        "--judge",
        choices=["pragmatist", "innovator", "user_advocate"],
        default="pragmatist",
        help="Judge personality"
    )
    
    # Batch analysis command
    batch_parser = subparsers.add_parser("batch", help="Analyze multiple requirements")
    batch_parser.add_argument("input_file", help="File containing requirements (one per line)")
    batch_parser.add_argument("--output", default="results.csv", help="Output file for results")
    batch_parser.add_argument(
        "--judge",
        choices=["pragmatist", "innovator", "user_advocate"],
        default="pragmatist",
        help="Judge personality for all analyses"
    )
    
    args = parser.parse_args()
    
    # Initialize ReqDefender
    defender = ReqDefender()
    
    # Handle commands
    if args.command == "analyze":
        # Run single analysis
        result = defender.analyze(
            args.requirement,
            debate_mode=args.mode,
            judge_personality=args.judge
        )
        
        # Print results
        print(f"\n{'='*60}")
        print(f"VERDICT: {result['verdict']}")
        print(f"Confidence: {result['confidence']:.1f}%")
        print(f"\nReasoning: {result['reasoning']}")
        
        if result.get('alternative'):
            print(f"\nAlternative: {result['alternative']}")
        
        if result.get('savings'):
            print(f"\nEstimated Savings: ${result['savings']:,.0f}")
        
        print(f"{'='*60}\n")
    
    elif args.command == "quick":
        # Run quick analysis
        result = defender.analyze(
            args.requirement,
            debate_mode="quick",
            judge_personality=args.judge
        )
        
        # Print concise results
        verdict_emoji = "✅" if result['verdict'] == "APPROVED" else "❌"
        print(f"\n{verdict_emoji} {result['verdict']} ({result['confidence']:.1f}% confidence)")
        
        if result.get('alternative'):
            print(f"💡 Alternative: {result['alternative']}")
    
    elif args.command == "batch":
        # Run batch analysis
        import csv
        
        # Read requirements from file
        with open(args.input_file, 'r') as f:
            requirements = [line.strip() for line in f if line.strip()]
        
        print(f"Analyzing {len(requirements)} requirements...")
        
        # Analyze each requirement
        results = []
        for i, req in enumerate(requirements, 1):
            print(f"[{i}/{len(requirements)}] Analyzing: {req[:50]}...")
            
            try:
                result = defender.analyze(
                    req,
                    debate_mode="quick",
                    judge_personality=args.judge
                )
                results.append({
                    "requirement": req,
                    "verdict": result['verdict'],
                    "confidence": result['confidence'],
                    "alternative": result.get('alternative', ''),
                    "savings": result.get('savings', 0)
                })
            except Exception as e:
                logger.error(f"Failed to analyze '{req}': {e}")
                results.append({
                    "requirement": req,
                    "verdict": "ERROR",
                    "confidence": 0,
                    "alternative": str(e),
                    "savings": 0
                })
        
        # Write results to CSV
        with open(args.output, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["requirement", "verdict", "confidence", "alternative", "savings"])
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\nResults saved to {args.output}")
        
        # Print summary
        approved = len([r for r in results if r['verdict'] == 'APPROVED'])
        rejected = len([r for r in results if r['verdict'] == 'REJECTED'])
        total_savings = sum(r.get('savings', 0) for r in results)
        
        print(f"\nSummary:")
        print(f"  Approved: {approved}")
        print(f"  Rejected: {rejected}")
        print(f"  Total Potential Savings: ${total_savings:,.0f}")
    
    else:
        # Run services based on mode
        if args.mode == "all":
            defender.run_all_services(args.interface)
        elif args.mode == "web":
            defender.run_streamlit(args.interface)
        elif args.mode == "rest":
            defender.run_rest_server()
        elif args.mode == "websocket":
            defender.run_websocket_server()
        elif args.mode == "debate":
            defender.run_debate_api()


if __name__ == "__main__":
    main()
#built with love
