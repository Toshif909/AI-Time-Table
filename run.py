"""
AI Timetable Generator — Entry Point
Run this file to start the application server.
"""
import uvicorn
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🧠 AI TIMETABLE GENERATOR")
    print("  Centre for Artificial Intelligence")
    print("=" * 60)
    print("\n  Starting server...")
    print("  Open your browser at: http://localhost:8000")
    print("  Press Ctrl+C to stop\n")

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
