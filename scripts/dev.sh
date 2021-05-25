#!/bin/bash
# Created by James Raphael Tiovalen (2020)

source "../env/bin/activate"
cd "../app"

if [[ $(sudo snap info ngrok | grep "installed") ]]; then
    echo "Ngrok is already installed!"
else
    echo "Ngrok is not yet installed. Installing the latest version using the Snap Store..."
    sudo snap install ngrok
fi

# Define ngrok authentication token
export AUTHTOKEN=<token>
ngrok authtoken $AUTHTOKEN

# Run ngrok server as background process
# Ensure that ngrok's port forwards to FastAPI's port
ngrok http 8000 &

# Run main bot code
uvicorn main:app --reload --port 8000
