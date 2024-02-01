FROM quay.io/keycloak/keycloak:latest
WORKDIR /opt/keycloak/

RUN mkdir -p /opt/keycloak/data/import

RUN ./bin/kc.sh build --db=postgres --http-relative-path=/oauth

COPY entrypoint.sh /opt/keycloak/

ENTRYPOINT [ "/opt/keycloak/entrypoint.sh" ]
