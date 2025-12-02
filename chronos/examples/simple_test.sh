#!/bin/bash
# Simple test script for chronos

echo "Starting simple test..."

# Test exec command
./chronos exec "Echo Test" -- echo "Hello from chronos!"

# Test start/end with nested exec
./chronos start "Build Phase"
./chronos exec -- echo "Building something..."
./chronos exec -- sleep 0.5
./chronos end "Build Phase"

# Test log command
./chronos start "Deploy"
./chronos log "Starting deployment process"
./chronos exec -- echo "Deploying..."
./chronos log "Deployment complete"
./chronos end "Deploy"

echo "Test completed!"
