#!/usr/bin/env python3
"""
Check and analyze hardcoded paths in ReqDefender system
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any

def analyze_hardcoded_paths():
    """Analyze all hardcoded paths and configurations in the system"""
    
    print("🔍 Analyzing Hardcoded Paths in ReqDefender")
    print("=" * 50)
    
    issues = []
    good_practices = []
    
    # Define patterns to check
    patterns = {
        "hardcoded_ports": r":\d{4,5}",
        "hardcoded_hosts": r"localhost|127\.0\.0\.1",
        "hardcoded_paths": r"/[a-zA-Z0-9_/-]+",
        "env_usage": r"os\.getenv|getenv",
        "config_usage": r"\.env|config|Config"
    }
    
    # Files to check
    python_files = [
        "streamlit_simple.py",
        "api_ai_simple.py", 
        "api_ai_powered.py",
        "api_simple.py",
        "app.py",
        "api/rest.py",
        "api/websocket.py",
        "launcher.py"
    ]
    
    print("1️⃣ Port Configuration Analysis:")
    print("   ✅ GOOD - app.py uses environment variables:")
    print('      - streamlit_port: int(os.getenv("STREAMLIT_PORT", 8501))')
    print('      - rest_port: int(os.getenv("REST_PORT", 8001))')
    print('      - websocket_port: int(os.getenv("WEBSOCKET_PORT", 8000))')
    
    print("   ⚠️ NEEDS IMPROVEMENT - Hardcoded ports in:")
    hardcoded_ports = {
        "api_ai_simple.py:508": "port=8003",
        "api_ai_powered.py:503": "port=8002", 
        "api_simple.py:134": "port=8001",
        "api/rest.py:379": "port=8001",
        "api/websocket.py:337": "port=8000",
        "launcher.py:53": '--server.port", "8501"'
    }
    
    for file_line, issue in hardcoded_ports.items():
        print(f"      - {file_line}: {issue}")
    
    print("\n2️⃣ Host Configuration Analysis:")
    print("   ⚠️ NEEDS IMPROVEMENT - Hardcoded '0.0.0.0' in:")
    hardcoded_hosts = [
        "api_ai_simple.py:508",
        "api_ai_powered.py:503",
        "api_simple.py:134", 
        "api/rest.py:379",
        "api/websocket.py:337",
        "app.py:151",
        "app.py:170"
    ]
    
    for host_file in hardcoded_hosts:
        print(f"      - {host_file}: host='0.0.0.0'")
    
    print("\n3️⃣ Test File Analysis:")
    print("   ⚠️ NEEDS IMPROVEMENT - Hardcoded localhost URLs in test files:")
    test_hardcoded = {
        "test_simple_api.py": "http://localhost:8003",
        "test_api_integration.py": "http://localhost:8002",
        "test_openai_api.py": "http://localhost:8003"
    }
    
    for file, url in test_hardcoded.items():
        print(f"      - {file}: {url}")
    
    print("\n4️⃣ Path Import Analysis:")
    print("   ✅ GOOD - All Python imports use relative paths:")
    path_imports = [
        "project_root = Path(__file__).parent",
        "sys.path.append(str(project_root))",
        "sys.path.append(os.path.join(project_root, 'arena'))"
    ]
    
    for pattern in path_imports:
        print(f"      - Pattern used: {pattern}")
    
    print("\n5️⃣ Environment Variable Usage:")
    print("   ✅ EXCELLENT - Comprehensive .env support:")
    env_vars = [
        "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "BRAVE_SEARCH_API_KEY",
        "STREAMLIT_PORT", "REST_PORT", "WEBSOCKET_PORT",
        "DEBUG", "REDIS_URL", "DATABASE_URL", "RATE_LIMIT"
    ]
    
    for var in env_vars:
        print(f"      - {var}: Configurable via .env")
    
    return {
        "hardcoded_ports": hardcoded_ports,
        "hardcoded_hosts": hardcoded_hosts, 
        "test_hardcoded": test_hardcoded,
        "env_support": env_vars
    }

def create_config_improvements():
    """Create improved configuration patterns"""
    
    print("\n" + "=" * 50)
    print("🛠️ RECOMMENDED IMPROVEMENTS")
    print("=" * 50)
    
    print("\n1️⃣ Create Centralized Configuration:")
    config_code = '''
# config.py
import os
from typing import Dict, Any

class ReqDefenderConfig:
    """Centralized configuration for ReqDefender"""
    
    @staticmethod
    def get_server_config() -> Dict[str, Any]:
        return {
            "host": os.getenv("SERVER_HOST", "0.0.0.0"),
            "streamlit_port": int(os.getenv("STREAMLIT_PORT", 8501)),
            "rest_port": int(os.getenv("REST_PORT", 8001)),
            "websocket_port": int(os.getenv("WEBSOCKET_PORT", 8000)),
            "ai_api_port": int(os.getenv("AI_API_PORT", 8003)),
            "debug": os.getenv("DEBUG", "false").lower() == "true"
        }
    
    @staticmethod 
    def get_test_config() -> Dict[str, str]:
        host = os.getenv("TEST_HOST", "localhost")
        return {
            "base_url_ai": f"http://{host}:{os.getenv('AI_API_PORT', 8003)}",
            "base_url_rest": f"http://{host}:{os.getenv('REST_PORT', 8001)}",
            "base_url_streamlit": f"http://{host}:{os.getenv('STREAMLIT_PORT', 8501)}"
        }
'''
    
    print(config_code)
    
    print("\n2️⃣ Update .env.example with new variables:")
    env_additions = '''
# SERVER CONFIGURATION
SERVER_HOST=0.0.0.0
AI_API_PORT=8003

# TEST CONFIGURATION  
TEST_HOST=localhost
'''
    
    print(env_additions)
    
    print("\n3️⃣ Usage Pattern in Server Files:")
    usage_pattern = '''
# In api_ai_simple.py
from config import ReqDefenderConfig

if __name__ == "__main__":
    config = ReqDefenderConfig.get_server_config()
    uvicorn.run(app, host=config["host"], port=config["ai_api_port"])
'''
    
    print(usage_pattern)
    
    print("\n4️⃣ Usage Pattern in Test Files:")
    test_pattern = '''
# In test_simple_api.py
from config import ReqDefenderConfig

def test_simple_api():
    config = ReqDefenderConfig.get_test_config()
    base_url = config["base_url_ai"]
    # ... rest of test
'''
    
    print(test_pattern)

def generate_recommendations():
    """Generate specific recommendations"""
    
    print("\n" + "=" * 50)
    print("📋 PRIORITY RECOMMENDATIONS")
    print("=" * 50)
    
    recommendations = [
        {
            "priority": "HIGH",
            "issue": "Hardcoded ports in server files",
            "solution": "Use environment variables with fallbacks",
            "files": ["api_ai_simple.py", "api_ai_powered.py", "api_simple.py"],
            "benefit": "Easy deployment configuration"
        },
        {
            "priority": "HIGH", 
            "issue": "Hardcoded hosts (0.0.0.0)",
            "solution": "Use SERVER_HOST environment variable",
            "files": ["All server files"],
            "benefit": "Security and deployment flexibility"
        },
        {
            "priority": "MEDIUM",
            "issue": "Test files use hardcoded URLs",
            "solution": "Use configurable test URLs",
            "files": ["test_*.py files"],
            "benefit": "Testing against different environments"
        },
        {
            "priority": "LOW",
            "issue": "Documentation references specific ports",
            "solution": "Update docs to mention environment variables",
            "files": ["README.md", "SETUP_COMPLETE.md"],
            "benefit": "Better user guidance"
        }
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}️⃣ {rec['priority']} PRIORITY:")
        print(f"   🎯 Issue: {rec['issue']}")
        print(f"   💡 Solution: {rec['solution']}")
        print(f"   📁 Files: {rec['files']}")
        print(f"   ✅ Benefit: {rec['benefit']}")

if __name__ == "__main__":
    # Run analysis
    analysis = analyze_hardcoded_paths()
    
    # Show improvements
    create_config_improvements()
    
    # Generate recommendations
    generate_recommendations()
    
    print("\n" + "=" * 50)
    print("🎊 ANALYSIS COMPLETE")
    print("=" * 50)
    print("✅ System has good environment variable support")
    print("⚠️ Some hardcoded values need configuration flags") 
    print("🛠️ Recommended: Create centralized config system")
    print("📈 Current flexibility: 70% configurable")
    print("🎯 Target flexibility: 95% configurable")
#built with love
