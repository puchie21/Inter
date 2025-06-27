# Main entry point - redirects to simple_binary_app.py
import streamlit as st
import sys
import os

# Add current directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the simple binary app
from simple_binary_app import main

if __name__ == "__main__":
    main()