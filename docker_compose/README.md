# docker compose readme

## Docker Compose

This directory contains separate docker-compose files for each of the services that are part of the project.

The directory 'core' contains the main docker-compose file that enable the publication of WIS2 data and metadata notifications.

The directory 'frontend' contains files for the web-based frontend services.

## Core

The following services are part of the core wis2box-services:

### wis2box-management

This is a set of python modules that provide the core functionality of the WIS2Box. The command that keeps the container running is:

```bash
wis2box pubsub subscribe
```

This command subscribes to the internal WIS2Box message broker on the topic wis2box/#. 

By default the internal WIS2Box message broker  also serve as the public-facing broker by setting = 

```bash
WIS2BOX_BROKER_PUBLIC=mqtt://${WIS2BOX_BROKER_USERNAME}:${WIS2BOX_BROKER_PASSWORD}@mosquitto:1883
```

### wis2box-broker

Mosquitto-service that provides the (internal) message broker for the WIS2Box. 

### wis2box-api

This is a pygeoapi instance that provides access to the WIS2Box data and metadata. For the source-code see github repository: https://github.com/wmo-im/wis2box-api

The default backend for the wis2box-api is provided by an elasticsearch container on the same (docker) network.

### wis2box-elasticsearch

An elasticsearch instance that provides the backend for the wis2box-api. 


