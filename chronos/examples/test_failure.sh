#!/bin/bash
# Test script that includes a failure

./chronos start "Setup"
./chronos exec -- echo "Setting up..."
./chronos end "Setup"

./chronos start "Build"
./chronos exec "Compile" -- echo "Compiling..."
./chronos exec "Test" -- sh -c 'echo "Running tests..."; exit 1'  # This will fail
./chronos end "Build"

./chronos start "Deploy"
./chronos exec -- echo "Deploying..."
./chronos end "Deploy"
