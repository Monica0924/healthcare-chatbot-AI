#!/usr/bin/env python3
"""
FastAPI Server Runner for AI Health Chatbot
Run this script to start the FastAPI server with Uvicorn
"""

import uvicorn
import os
import sys
from main import init_db

def main():
    """Initialize database and start the server"""
    print("🚀 Starting AI Health Chatbot API Server...")
    
    # Initialize database
    print("📊 Initializing database...")
    init_db()
    print("✅ Database initialized successfully")
    
    # Start server
    print("🌐 Starting server on http://127.0.0.1:5000")
    print("📚 API Documentation available at http://127.0.0.1:5000/docs")
    print("🩺 Doctor Panel: http://127.0.0.1:5000/static/doctor-panel.html")
    print("🏠 Main Site: http://127.0.0.1:5000/static/index.html")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=5000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
