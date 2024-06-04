.. _downloading-data:

Downloading data from WIS2
==========================

Overview
--------

This section provides guidance how to download data from WIS2 Global Services. 

WIS2 Global Services include a Global Broker that provides users the ability to subscribe to data (via topics) and download to their
local environment / workstation / decision support system from the WIS2 Global Cache.

wis2-downloader
---------------

wis2box enables subscribe and data download workflow the WIS2 network, by using the ``wis2-downloader`` container, inside of which runs the `wis2-downloader tool <https://github.com/wmo-im/wis2-downloader`_

``wis2-downloader`` is a Python package that provides subscription and download capability, by connecting to pre-defined MQTT-broker.

The following environment variables are used by the ``wis2-downloader``:

- ``DOWNLOAD_BROKER_HOST``: The hostname of the MQTT-broker to connect to. Defaults to ``globalbroker.meteo.fr``
- ``DOWNLOAD_BROKER_PORT``: The port of the MQTT-broker to connect to. Defaults to ``443`` (HTTPS for websockets)
- ``DOWNLOAD_BROKER_USERNAME``: The username to use to connect to the MQTT-broker. Defaults to ``everyone``
- ``DOWNLOAD_BROKER_PASSWORD``: The password to use to connect to the MQTT-broker. Defaults to ``everyone``
- ``DOWNLOAD_BROKER_PROTOCOL``: The protocol to use to connect to the MQTT-broker. Defaults to ``websockets``
- ``DOWNLOAD_RETENTION_PERIOD_HOURS``: The retention period in hours for the downloaded data. Defaults to ``24``
- ``DOWNLOAD_WORKERS``: The number of download workers to use. Defaults to ``8``. Determines the number of parallel downloads.

To override the default configuration, you can set the environment variables in the wis2box.env file.

By default the wis2-downloader is not subscribed to any topics. You can add subscriptions using the API endpoint, as described below.

The files downloaded by the wis2-downloader will be saved in `${WIS2BOX_HOST_DATADIR}/downloads`, where `${WIS2BOX_HOST_DATADIR}` is the directory on your host you defined in the `wis2box.env` file.

Maintaining and Monitoring Subscriptions
----------------------------------------

The wis2-downloader has an API-endpoint that is proxied on the path `/wis2-downloader` on the wis2box host-url. This endpoint can be used to add, delete and list subscriptions.

The endpoint is secured using an API token, that can be created using the 'wis2box auth' command inside the wis2box-management container as follows:

```bash
python3 wis2box.ctl.py execute wis2box auth add-token --path wis2-downloader -y
```

Record the generated token, so you can use it to authenticate requests to the API.

Listing subscriptions
~~~~~~~~~~~~~~~~~~~~~

To list the active subscriptions, a GET request can be made to the `wis2-downloader/list` endpoint, making sure to pass the API token as a header:

```bash
curl http://localhost/wis2-downloader/list -H "Authorization: Bearer <API-token>"
```

The list of the currently active subscriptions should be returned as a JSON object.

Adding subscriptions
~~~~~~~~~~~~~~~~~~~~

Subscriptions can be added via a GET request to the `./add` endpoint that is proxied on /wis2-downloader on the wis2box host, with the following form:

```bash
curl http://localhost/wis2-downloader/add?topic=<topic-name>&target=<download-directory> -H "Authorization: Bearer <API-token>"
```

- `topic` specifies the topic to subscribe to. *Special characters (+, #) must be URL encoded, i.e. `+` = `%2B`, `#` = `%23`.*
- `target` specifies the directory to save the downloads to, relative to `download_dir` from `config.json`. *If this is not provided, the directory will default to that of the topic hierarchy.*

For example:
```bash
curl http://localhost/wis2-downloader/add?topic=cache/a/wis2/%2B/data/core/weather/%23&target=example_data -H "Authorization: Bearer <API-token>"
```

The list of active subscriptions after addition should be returned as a JSON object.

Deleting subscriptions
~~~~~~~~~~~~~~~~~~~~~~

Subscriptions are deleted similarly via a GET request to the `./delete` endpoint, with the following form:
```bash
curl http://<flask-host>:<flask-port>/delete?topic=<topic-name> -H "Authorization: Bearer <API-token>"
```

For example:
```bash
curl http://localhost:8080/delete?topic=cache/a/wis2/%2B/data/core/weather/%23 -H "Authorization: Bearer <API-token>"
```

The list of active subscriptions after deletion should be returned as a JSON object.



