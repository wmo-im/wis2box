FROM quay.io/keycloak/keycloak:20.0.3
WORKDIR /opt/keycloak/

RUN ./bin/kc.sh build --db=postgres

# WIP-FIXME: Downloading oauth2-proxy **uncompressed** binary from non-standard location
# To fix see https://www.keycloak.org/server/containers to add `tar` via `dnf` package manager
USER root
RUN curl -Lo /opt/keycloak/oauth2-proxy https://github.com/isedwards/wis2box-auth/raw/oauth2-proxy-bin/oauth2-proxy && \
    chown keycloak /opt/keycloak/oauth2-proxy && chmod +x /opt/keycloak/oauth2-proxy
COPY entrypoint.sh /opt/keycloak/
RUN chown keycloak /opt/keycloak/entrypoint.sh && chmod +x /opt/keycloak/entrypoint.sh
USER keycloak

# Replace standard entrypoint ("/opt/keycloak/bin/kc.sh")
ENTRYPOINT [ "/opt/keycloak/entrypoint.sh" ]
