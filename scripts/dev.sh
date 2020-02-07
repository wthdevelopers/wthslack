#!/bin/bash
# Created by James Raphael Tiovalen (2020)

source "../env/bin/activate"
cd "../app"

# Define ngrok authentication token
export AUTHTOKEN=<token>
ngrok authtoken $AUTHTOKEN

# Run ngrok server as background process
# Ensure that ngrok's port forwards to FastAPI's port
ngrok http 8000 &

# Run main bot code
uvicorn main:app --reload --port 8000
