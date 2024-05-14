# docker minimum readme

This directory provides provided separate docker-compose files to start the minimum required wis2box-services without relying on the full wis2box-stack as managed by wis2box-ctl.py.

It is intended to allow "power-users" to more easily re-use services and configuration in a customized wis2box environment.

To start the minimum required services, run the following command:

```bash

docker compose -f docker-compose.minio.yml -f docker-compose.wis2box-management.yml -f docker-compose.mosquitto.yml -f docker-compose.elasticsearch.yml -f docker-compose.wis2box-api.yml -p wis2box-minimum up -d

```

This starts the stack and defines the project name as `wis2box-minimum`.

You can see the environment-variables used by each wis2box-service in the 'environment' section of the docker-compose files.

### wis2box-management

This service uses an Ubuntu base image and installs the wis2box python classes defined in the wis2box-management directory of this repository. Within the container a set of commands are available to manage the wis2box. The container is listening to the internal message broker for messages on the topic wis2box/#. The storage service should be configured to send messages to this topic when objects are added to the storage to allow the wis2box-management to trigger the workflow defined by the data-mappings configuration for each dataset.

Note that the command that keeps the container running is:

```bash
wis2box pubsub subscribe
```

The wis2box pubsub class defined in wis2box-management/wis2box/pubsub/ determines what actions are taken when a message is received on the internal message broker. 

### mosquitto

Mosquitto-service that provides the internal message broker for the WIS2Box.

Note that in the standard wis2box-stack the internal broker is also used as the external broker.

The wis2box-broker image is defined by the Dockerfile in the wis2box-broker directory of this repository.

### MinIO

MinIO is used to provide an http-compatible storage endpoint to serve the data and metadata published by wis2box. It is an S3-compatible object storage server. 

Notifications are sent to the internal message broker when objects are added to the storage to trigger the workflow defined by the data-mappings configuration for each dataset.

### wis2box-api

This is a pygeoapi instance that provides access to the WIS2Box data and metadata. For the source-code see github repository: https://github.com/wmo-im/wis2box-api

The backend for the wis2box-api is provided by elasticsearch.

Note that wis2box-api service includes the eccodes library to allow the following conversion to bufr.

Note that wis2box-api provides access to the collections 'stations' and 'discovery-metadata':
- 'stations' is a collection of station metadata used when processing data using csv2bufr, synop2bufr and bufr2bufr
- 'discovery-metadata' is a collection of datasets configured in the wis2box, with each dataset containing metadata that describes the dataset and the data-mappings that define the workflow to be triggered when data is added to the storage.


### elasticsearch

An elasticsearch instance that provides the backend for the wis2box-api.


