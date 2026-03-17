#!/bin/bash

# GitHub MCP Server Launcher

echo "==================================="
echo "  GitHub MCP Server"
echo "==================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create a .env file with your GITHUB_TOKEN"
    echo ""
    echo "Steps:"
    echo "1. cp .env.example .env"
    echo "2. Edit .env and add your GitHub token"
    echo ""
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN is not set in .env file"
    exit 1
fi

echo "✅ Configuration loaded"
echo "🚀 Starting GitHub MCP Server..."
echo ""

# Run the server
python -m server.main
