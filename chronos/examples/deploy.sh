#!/bin/bash
# Example script demonstrating chronos usage

# Helper to run chronos commands
CHRONOS="./chronos"

# Start Build phase
$CHRONOS start "Build"

# Run install
$CHRONOS exec "Install deps" -- sleep 1

# Run compile
$CHRONOS exec "Compile" -- sh -c 'echo "Compiling source files..."; sleep 0.5; echo "Done compiling"'

$CHRONOS end "Build"

# Start Test phase
$CHRONOS start "Test"

$CHRONOS exec -- sh -c 'echo "Running unit tests..."; sleep 0.5; echo "All tests passed!"'

$CHRONOS end "Test"

# Start Deploy phase
$CHRONOS start "Deploy"

$CHRONOS log "Deploying to production..."
$CHRONOS exec "Push to server" -- sh -c 'echo "Uploading files..."; sleep 0.5; echo "Upload complete"'

$CHRONOS end "Deploy"

echo "Deployment complete!"
