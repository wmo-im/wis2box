FROM quay.io/keycloak/keycloak:20.0.3
WORKDIR /opt/keycloak/

# WIP-FIXME: Automatically create realm and client settings on build
# COPY wis2box-keycloak.json /opt/keycloak/data/import/wis2box-keycloak.json
# Moving realm import to start up
# https://www.keycloak.org/server/importExport#_importing_a_realm_during_startup
# RUN ./bin/kc.sh import --file /opt/keycloak/data/import/wis2box-keycloak.json && ./bin/kc.sh build --db=postgres

RUN ./bin/kc.sh build --db=postgres
