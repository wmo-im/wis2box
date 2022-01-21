FROM eclipse-mosquitto

RUN ln -s /mosquitto /data/wis2node/mosquitto

COPY mosquitto.conf /mosquitto/config/mosquitto.conf
COPY entrypoint.sh /docker-entrypoint.sh

RUN chmod +x /docker-entrypoint.sh
