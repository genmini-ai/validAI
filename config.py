#!/usr/bin/env python3
"""
Centralized configuration for ReqDefender system
Eliminates hardcoded paths and provides environment-based configuration
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ReqDefenderConfig:
    """Centralized configuration manager for ReqDefender"""
    
    @staticmethod
    def get_server_config() -> Dict[str, Any]:
        """Get server configuration with environment variable support"""
        return {
            # Network Configuration
            "host": os.getenv("SERVER_HOST", "0.0.0.0"),
            "streamlit_port": int(os.getenv("STREAMLIT_PORT", 8501)),
            "rest_port": int(os.getenv("REST_PORT", 8001)),
            "websocket_port": int(os.getenv("WEBSOCKET_PORT", 8000)),
            "ai_api_port": int(os.getenv("AI_API_PORT", 8003)),
            "ai_api_v2_port": int(os.getenv("AI_API_V2_PORT", 8002)),
            "debate_api_port": int(os.getenv("DEBATE_API_PORT", 8004)),
            
            # Application Configuration
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "disable_cache": os.getenv("DISABLE_CACHE", "false").lower() == "true",
            "force_fresh_responses": os.getenv("FORCE_FRESH_RESPONSES", "false").lower() == "true",
            "rate_limit": int(os.getenv("RATE_LIMIT", 60)),
            "max_debate_duration": int(os.getenv("MAX_DEBATE_DURATION", 300)),
            
            # Default Settings
            "default_judge": os.getenv("DEFAULT_JUDGE", "pragmatist"),
            "default_intensity": os.getenv("DEFAULT_INTENSITY", "standard"),
        }
    
    @staticmethod 
    def get_test_config() -> Dict[str, str]:
        """Get test configuration with configurable endpoints"""
        host = os.getenv("TEST_HOST", "localhost")
        config = ReqDefenderConfig.get_server_config()
        
        return {
            "host": host,
            "base_url_streamlit": f"http://{host}:{config['streamlit_port']}",
            "base_url_rest": f"http://{host}:{config['rest_port']}",
            "base_url_websocket": f"ws://{host}:{config['websocket_port']}",
            "base_url_ai_api": f"http://{host}:{config['ai_api_port']}",
            "base_url_ai_api_v2": f"http://{host}:{config['ai_api_v2_port']}",
            "timeout": int(os.getenv("TEST_TIMEOUT", 30))
        }
    
    @staticmethod
    def get_ai_config() -> Dict[str, Any]:
        """Get AI service configuration"""
        return {
            # API Keys
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
            "brave_search_api_key": os.getenv("BRAVE_SEARCH_API_KEY"),
            "google_api_key": os.getenv("GOOGLE_API_KEY"),
            "google_cse_id": os.getenv("GOOGLE_CSE_ID"),
            
            # AI Configuration
            "max_tokens": int(os.getenv("AI_MAX_TOKENS", 800)),
            "temperature": float(os.getenv("AI_TEMPERATURE", 0.7)),
            "model_preference": os.getenv("AI_MODEL_PREFERENCE", "anthropic"),  # anthropic, openai, both
            
            # Search Configuration
            "max_evidence_sources": int(os.getenv("MAX_EVIDENCE_SOURCES", 10)),
            "search_timeout": int(os.getenv("SEARCH_TIMEOUT", 15)),
        }
    
    @staticmethod
    def get_database_config() -> Dict[str, Optional[str]]:
        """Get database configuration"""
        return {
            "redis_url": os.getenv("REDIS_URL"),
            "database_url": os.getenv("DATABASE_URL"),
            "sentry_dsn": os.getenv("SENTRY_DSN"),
            "analytics_api_key": os.getenv("ANALYTICS_API_KEY"),
        }
    
    @staticmethod
    def get_uvicorn_config(service: str = "main") -> Dict[str, Any]:
        """Get uvicorn server configuration for different services"""
        server_config = ReqDefenderConfig.get_server_config()
        
        port_mapping = {
            "streamlit": server_config["streamlit_port"],
            "rest": server_config["rest_port"],
            "websocket": server_config["websocket_port"],
            "ai_api": server_config["ai_api_port"],
            "ai_api_v2": server_config["ai_api_v2_port"],
            "debate_api": server_config["debate_api_port"],
            "main": server_config["rest_port"]  # Default
        }
        
        return {
            "host": server_config["host"],
            "port": port_mapping.get(service, server_config["rest_port"]),
            "reload": server_config["debug"],  # Enable reload in debug mode
            "access_log": server_config["debug"]
        }
    
    @staticmethod
    def validate_config() -> Dict[str, bool]:
        """Validate configuration and return status"""
        ai_config = ReqDefenderConfig.get_ai_config()
        
        return {
            "has_openai": bool(ai_config["openai_api_key"] and "your_openai" not in ai_config["openai_api_key"]),
            "has_anthropic": bool(ai_config["anthropic_api_key"] and "your_anthropic" not in ai_config["anthropic_api_key"]),
            "has_brave_search": bool(ai_config["brave_search_api_key"] and "your_brave" not in ai_config["brave_search_api_key"]),
            "has_google_search": bool(ai_config["google_api_key"] and "your_google" not in ai_config["google_api_key"]),
            "has_llm": False,  # Will be set below
            "has_search": False,  # Will be set below
            "production_ready": False  # Will be set below
        }
    
    @classmethod
    def get_system_status(cls) -> Dict[str, Any]:
        """Get comprehensive system status"""
        validation = cls.validate_config()
        server_config = cls.get_server_config()
        
        # Update computed values
        validation["has_llm"] = validation["has_openai"] or validation["has_anthropic"]
        validation["has_search"] = validation["has_brave_search"] or True  # DuckDuckGo always available
        validation["production_ready"] = validation["has_llm"] and validation["has_search"]
        
        return {
            "validation": validation,
            "config": {
                "server": server_config,
                "ports": {
                    "streamlit": server_config["streamlit_port"],
                    "rest_api": server_config["rest_port"], 
                    "websocket": server_config["websocket_port"],
                    "ai_api": server_config["ai_api_port"],
                    "ai_api_v2": server_config["ai_api_v2_port"]
                },
                "ai_engines": {
                    "openai_available": validation["has_openai"],
                    "anthropic_available": validation["has_anthropic"],
                    "search_available": validation["has_search"]
                }
            }
        }

# Convenience functions for backward compatibility
def get_port(service: str) -> int:
    """Get port for a specific service"""
    config = ReqDefenderConfig.get_server_config()
    port_mapping = {
        "streamlit": config["streamlit_port"],
        "rest": config["rest_port"],
        "websocket": config["websocket_port"],
        "ai_api": config["ai_api_port"],
        "ai_api_v2": config["ai_api_v2_port"]
    }
    return port_mapping.get(service, config["rest_port"])

def get_host() -> str:
    """Get server host"""
    return ReqDefenderConfig.get_server_config()["host"]

def get_base_url(service: str, host: Optional[str] = None) -> str:
    """Get base URL for a service"""
    if host is None:
        host = os.getenv("TEST_HOST", "localhost")
    
    port = get_port(service)
    protocol = "ws" if service == "websocket" else "http"
    return f"{protocol}://{host}:{port}"

# Example usage and testing
if __name__ == "__main__":
    print("🔧 ReqDefender Configuration System")
    print("=" * 40)
    
    # Show system status
    status = ReqDefenderConfig.get_system_status()
    
    print("🌐 Server Configuration:")
    server = status["config"]["server"]
    print(f"   Host: {server['host']}")
    print(f"   Debug: {server['debug']}")
    
    print("\n📡 Port Configuration:")
    ports = status["config"]["ports"]
    for service, port in ports.items():
        print(f"   {service.title()}: {port}")
    
    print("\n🤖 AI Configuration:")
    ai = status["config"]["ai_engines"]
    print(f"   OpenAI: {'✅ Available' if ai['openai_available'] else '❌ Missing'}")
    print(f"   Anthropic: {'✅ Available' if ai['anthropic_available'] else '❌ Missing'}")
    print(f"   Search: {'✅ Available' if ai['search_available'] else '❌ Missing'}")
    
    print("\n🎯 System Status:")
    validation = status["validation"]
    print(f"   LLM Ready: {'✅ Yes' if validation['has_llm'] else '❌ No'}")
    print(f"   Search Ready: {'✅ Yes' if validation['has_search'] else '❌ No'}")
    print(f"   Production Ready: {'✅ Yes' if validation['production_ready'] else '❌ No'}")
    
    print("\n🔗 Service URLs (for testing):")
    test_config = ReqDefenderConfig.get_test_config()
    services = ["streamlit", "rest", "websocket", "ai_api", "ai_api_v2"]
    for service in services:
        url_key = f"base_url_{service.replace('_', '_')}"
        if url_key in test_config:
            print(f"   {service.title()}: {test_config[url_key]}")
#built with love
