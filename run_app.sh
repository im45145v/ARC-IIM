#!/bin/bash
# Startup script for Alumni Management System

# Set PYTHONPATH to include the project root
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Run the Streamlit application
streamlit run alumni_system/frontend/app.py
