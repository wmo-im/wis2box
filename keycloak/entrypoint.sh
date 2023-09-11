#!/bin/bash
# Replacing the default keycloak entrypoint with a version that manages both
# keycloak and oauth2-proxy processes. This script is PID 1 in the container.

# Start keycloak in the background with the passed arguments
/opt/keycloak/bin/kc.sh "$@" &

# Get the PID of the Keycloak process
keycloak_pid=$!

# Wait for Keycloak to be accessible
while ! curl -s http://localhost:8180/auth > /dev/null; do
  echo "Waiting for Keycloak to start..."
  sleep 5
done

# Start oauth2-proxy in the background
# If you don't whitelist keycloak's domain (and port) then redirects to keycloak will be ignored
# WIP-FIXME: get keycloak location from envvar and remove above comment
/opt/keycloak/oauth2-proxy \
  --email-domain=* \
  --http-address=":4180" \
  --insecure-oidc-allow-unverified-email \
  --skip-provider-button \
  --set-xauthrequest \
  --pass-access-token \
  --set-authorization-header \
  --whitelist-domain localhost:8180 \
  &

# Get the PID of the oauth2-proxy process
oauth2_proxy_pid=$!

# Function to handle termination and stop the services gracefully
terminate_processes() {
  # Kill the oauth2-proxy process
  kill "$oauth2_proxy_pid" || true
  
  # Kill the Keycloak process
  kill "$keycloak_pid" || true

  # Wait for background processes to shut down
  wait
  exit 0
}

# Trap SIGTERM and SIGINT signals and call terminate_processes
trap 'terminate_processes' SIGTERM SIGINT

# Wait indefinitely (for background processes) while keeping the script alive
wait
