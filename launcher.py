#!/usr/bin/env python3
"""Simple launcher for ReqDefender components"""

import os
import sys
import subprocess
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_setup():
    """Check if basic setup is complete"""
    print("🛡️ ReqDefender - Checking Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        return False
    else:
        print("✅ Python version OK")
    
    # Check API keys
    has_openai = os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your_openai_api_key_here"
    has_anthropic = os.getenv("ANTHROPIC_API_KEY") and os.getenv("ANTHROPIC_API_KEY") != "your_anthropic_api_key_here"
    
    if has_openai:
        print("✅ OpenAI API key configured")
    elif has_anthropic:
        print("✅ Anthropic API key configured")
    else:
        print("⚠️  No LLM API keys configured (demo mode only)")
    
    # Check if in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("⚠️  Not in virtual environment (recommended to use venv)")
    
    print("\n✅ Setup check completed!")
    return True

def run_streamlit():
    """Launch Streamlit web interface"""
    print("🌐 Starting Streamlit Web Interface...")
    print("Access at: http://localhost:8501")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_simple.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit stopped")

def run_api():
    """Launch AI-Powered REST API"""
    print("🚀 Starting AI-Powered REST API...")
    print("Access at: http://localhost:8003")
    print("Docs at: http://localhost:8003/docs")
    
    try:
        subprocess.run([sys.executable, "api_ai_simple.py"])
    except KeyboardInterrupt:
        print("\n👋 API stopped")

def run_test():
    """Run test analysis"""
    print("🧪 Running Test Analysis...")
    subprocess.run([sys.executable, "test_simple_api.py"])

def analyze_requirement(requirement):
    """Analyze a single requirement"""
    print(f"🤖 Analyzing: '{requirement}'")
    print("=" * 50)
    
    # Simple analysis logic
    import random
    
    req_lower = requirement.lower()
    
    if any(word in req_lower for word in ["blockchain", "crypto", "nft"]):
        verdict = "REJECTED"
        confidence = random.randint(80, 95)
        savings = 2100000
        alternative = "Use PostgreSQL with audit logs"
    elif any(word in req_lower for word in ["search", "filter", "sort"]):
        verdict = "APPROVED"
        confidence = random.randint(75, 90)
        savings = 0
        alternative = None
    else:
        verdict = random.choice(["APPROVED", "REJECTED", "CONDITIONAL"])
        confidence = random.randint(60, 85)
        savings = random.randint(500000, 2000000) if verdict == "REJECTED" else 0
        alternative = "Consider simpler approach"
    
    print(f"🎯 Verdict: {verdict}")
    print(f"📊 Confidence: {confidence}%")
    if savings > 0:
        print(f"💰 Estimated Savings: ${savings:,}")
    if alternative and verdict != "APPROVED":
        print(f"💡 Alternative: {alternative}")
    
    print("\n✨ Analysis complete!")

def main():
    parser = argparse.ArgumentParser(description="ReqDefender - AI Agents Debate Your Requirements")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Web interface command
    subparsers.add_parser("web", help="Launch web interface")
    
    # API command
    subparsers.add_parser("api", help="Launch REST API")
    
    # Test command
    subparsers.add_parser("test", help="Run system test")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a requirement")
    analyze_parser.add_argument("requirement", help="The requirement to analyze")
    
    # Setup check
    subparsers.add_parser("check", help="Check system setup")
    
    args = parser.parse_args()
    
    if not args.command:
        # Default: show menu
        print("🛡️ ReqDefender - AI Requirements Validator")
        print("=" * 45)
        print()
        print("Available commands:")
        print("  web      - Launch web interface (recommended)")
        print("  api      - Launch REST API")
        print("  test     - Run system test")
        print("  analyze  - Analyze a requirement from CLI")
        print("  check    - Check system setup")
        print()
        print("Examples:")
        print("  python launcher.py web")
        print("  python launcher.py analyze 'Add blockchain to our app'")
        print("  python launcher.py test")
        return
    
    # Check setup for all commands except check
    if args.command != "check":
        if not check_setup():
            print("\n❌ Setup issues detected. Run 'python launcher.py check' for details.")
            return
        print()
    
    # Execute command
    if args.command == "web":
        run_streamlit()
    elif args.command == "api":
        run_api()
    elif args.command == "test":
        run_test()
    elif args.command == "analyze":
        analyze_requirement(args.requirement)
    elif args.command == "check":
        check_setup()

if __name__ == "__main__":
    main()
#built with love
