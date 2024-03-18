#!/bin/bash
# entrypoint.sh

# Import configuration to built version (using --optimized flag)
/opt/keycloak/bin/kc.sh import --optimized --file /opt/keycloak/data/import/keycloak-conf.json

# Run original entrypoint and pass all parameters
/opt/keycloak/bin/kc.sh "$@"
