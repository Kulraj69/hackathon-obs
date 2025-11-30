#!/bin/bash
cd /Users/kulraj/hackathon-diary
source venv/bin/activate # Assuming venv is used, or just use python3
python3 main.py >> agent.log 2>&1
