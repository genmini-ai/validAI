#!/bin/bash
# Quick start script for ReqDefender Multi-Round Debate System

set -e

echo "🎭 ReqDefender Multi-Round Debate System"
echo "========================================"

# Check if API keys are set
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY"
    echo ""
    echo "Example:"
    echo "export OPENAI_API_KEY='sk-proj-your_key_here'"
    echo "export ANTHROPIC_API_KEY='sk-ant-api03-your_key_here'"
    exit 1
fi

# Check Python dependencies
echo "📦 Checking dependencies..."
python3 -c "import streamlit, anthropic, openai, fastapi, aiohttp" 2>/dev/null || {
    echo "❌ Missing dependencies. Installing..."
    python3 -m pip install streamlit anthropic openai python-dotenv duckduckgo-search langchain-community fastapi uvicorn aiohttp
}

echo "✅ Dependencies ready!"
echo ""

# Start services based on argument
case "${1:-all}" in
    "api")
        echo "🚀 Starting Multi-Round Debate API only..."
        echo "   API will be available at: http://localhost:8004"
        echo ""
        python3 api_debate.py
        ;;
    "web")
        echo "🚀 Starting Streamlit Web Interface only..."
        echo "   Make sure api_debate.py is running on port 8004"
        echo "   Web interface will be available at: http://localhost:8501"
        echo ""
        python3 -m streamlit run streamlit_debate.py --server.address 0.0.0.0
        ;;
    "all"|*)
        echo "🚀 Starting complete Multi-Round Debate system..."
        echo ""
        echo "   Services will be available at:"
        echo "   📱 Web Interface: http://localhost:8501"
        echo "   🎭 Debate API: http://localhost:8004"
        echo "   📊 REST API: http://localhost:8001"
        echo ""
        python3 app.py --interface debate
        ;;
esac
#built with love
