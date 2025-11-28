#!/bin/bash
# Combined script to add alumni and scrape their LinkedIn profiles

echo "================================================"
echo "Alumni Management System - Add & Scrape"
echo "================================================"
echo ""

# Step 1: Add alumni to database
echo "Step 1: Adding alumni records to database..."
python3 scripts/add_alumni_batch.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to add alumni records"
    exit 1
fi

echo ""
echo "================================================"
echo ""

# Step 2: Scrape LinkedIn profiles
echo "Step 2: Scraping LinkedIn profiles..."
python3 scripts/scrape_new_alumni.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to scrape LinkedIn profiles"
    exit 1
fi

echo ""
echo "================================================"
echo "✨ All done! Alumni added and profiles scraped."
echo "================================================"
