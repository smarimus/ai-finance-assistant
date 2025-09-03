#!/usr/bin/env python3
"""
AI Finance Assistant - Phase 4 Complete
Multi-tab interface with Portfolio Analysis, Market Data, Chat, and Goals
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the main app class
from src.web_app.main import FinanceAssistantApp

def main():
    """Main entry point for the AI Finance Assistant"""
    try:
        # Create and run the application
        app = FinanceAssistantApp()
        app.run()
        
    except Exception as e:
        st.error(f"Error starting AI Finance Assistant: {str(e)}")
        st.markdown("""
        ### Troubleshooting
        
        If you're seeing this error, try:
        1. Make sure all dependencies are installed: `pip install -r requirements.txt`
        2. Check if the OpenAI API key is set: `export OPENAI_API_KEY=your_key`
        3. Verify the vector database exists: `python scripts/vector_db/build_vector_db.py`
        
        For basic functionality, the app will work with mock components if real ones aren't available.
        """)
        
        # Show debug info
        with st.expander("Debug Information"):
            st.text(f"Error: {str(e)}")
            st.text(f"Python path: {sys.path}")
            st.text(f"Current directory: {os.getcwd()}")

if __name__ == "__main__":
    main()
