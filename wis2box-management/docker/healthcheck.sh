#!/bin/bash
# Custom health check script

# Check if pubsub subscribe process is running
if ps aux | grep '/usr/bin/python3 /usr/local/bin/wis2box pubsub subscribe' | grep -v grep; then
  exit 0 # Process found, container is healthy
else
  exit 1 # Process not found, container is not healthy
fi