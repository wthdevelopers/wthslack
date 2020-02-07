#!/bin/bash
# Created by James Raphael Tiovalen (2020)

# Activate virtual environment and install dependencies
sudo apt install -y python3.7
sudo python3.7 -m venv "../env"
source "../env/bin/activate"
sudo pip install -r "../requirements-dev.txt"

# Run all tests
cd ..
python -m pytest
