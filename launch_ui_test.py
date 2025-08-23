#!/usr/bin/env python3
"""
Simple launcher for UI testing that avoids complex dependencies
"""

import subprocess
import sys
import os

def launch_ui_test():
    """Launch the UI test application"""
    print("🚀 Launching ReqDefender UI Test")
    print("=" * 50)
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    print(f"📁 Project directory: {project_dir}")
    print("🔧 Activating virtual environment...")
    
    # Run the UI test
    cmd = [
        "streamlit", "run", "test_ui_improvements.py", 
        "--server.port", "8501",
        "--server.headless", "false"
    ]
    
    print(f"🌟 Starting Streamlit: {' '.join(cmd)}")
    print("🌐 UI will be available at: http://localhost:8501")
    print("💡 This test shows the improved evidence card visibility")
    print()
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching UI: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 UI test stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    launch_ui_test()
#built with love
