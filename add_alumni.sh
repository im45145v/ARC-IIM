#!/bin/bash
# Quick script to add the two alumni records

echo "🎓 Adding Alumni Records..."
echo ""

python3 scripts/add_alumni_batch.py

echo ""
echo "✨ Done! You can now view them in the dashboard."
echo ""
echo "To start the app, run:"
echo "  streamlit run alumni_system/frontend/app.py"
