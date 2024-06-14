.. _downloading-data:

Downloading data from WIS2
==========================

Overview
--------

This section provides guidance how to download data from WIS2 Global Services. 

WIS2 Global Services include a Global Broker that provides users the ability to subscribe to data (via topics) and download to their
local environment / workstation / decision support system from the WIS2 Global Cache.

wis2downloader
---------------

wis2box enables subscribe and data download workflow the WIS2 network, by using the ``wis2downloader`` container, inside of which runs the `wis2downloader tool <https://github.com/wmo-im/wis2downloader`_

``wis2downloader`` is a Python package that provides subscription and download capability, by connecting to pre-defined MQTT-broker.

The following environment variables are used by the ``wis2downloader``:

- ``DOWNLOAD_BROKER_HOST``: The hostname of the MQTT-broker to connect to. Defaults to ``globalbroker.meteo.fr``
- ``DOWNLOAD_BROKER_PORT``: The port of the MQTT-broker to connect to. Defaults to ``443`` (HTTPS for websockets)
- ``DOWNLOAD_BROKER_USERNAME``: The username to use to connect to the MQTT-broker. Defaults to ``everyone``
- ``DOWNLOAD_BROKER_PASSWORD``: The password to use to connect to the MQTT-broker. Defaults to ``everyone``
- ``DOWNLOAD_BROKER_TRANSPORT``: ``websockets`` or ``tcp``, the transport-mechanism to use to connect to the MQTT-broker. Defaults to ``websockets``,
- ``DOWNLOAD_RETENTION_PERIOD_HOURS``: The retention period in hours for the downloaded data. Defaults to ``24``
- ``DOWNLOAD_WORKERS``: The number of download workers to use. Defaults to ``8``. Determines the number of parallel downloads.
- ``DOWNLOAD_MIN_FREE_SPACE_GB``: The minimum free space in GB to keep on the volume hosting the downloads. Defaults to ``1``.

To override the default configuration, you can set the environment variables in the wis2box.env file.

By default the wis2downloader is not subscribed to any topics. You can add subscriptions using the `wis2box downloader` commands, which will call the API over the internal docker network.

The files downloaded by the wis2downloader will be saved in `${WIS2BOX_HOST_DATADIR}/downloads`, where `${WIS2BOX_HOST_DATADIR}` is the directory on your host you defined in the `wis2box.env` file.

Maintaining and Monitoring Subscriptions
----------------------------------------

The wis2downloader has an API-endpoint that can be used to add, delete and list subscriptions. 

You can use the `wis2box downloader` commands to interact with the API, which will call the API over the internal docker network.

The next sections describe how to use the `wis2box downloader` commands to list, add and delete subscriptions.

Listing subscriptions
~~~~~~~~~~~~~~~~~~~~~

To list the current subscriptions, you can use the following command:

```
python3 wis2box.ctl.py execute wis2box downloader list-subscriptions
```

This will return a JSON object with the current subscriptions.

Adding a subscription
~~~~~~~~~~~~~~~~~~~~~

To add a subscription, you can use the following command:

```
python3 wis2box.ctl.py execute wis2box downloader add-subscription --topic <topic>
```

This will add a subscription to the topic you specify and return the JSON object with the current subscriptions.

Deleting a subscription
~~~~~~~~~~~~~~~~~~~~~~~

To delete a subscription, you can use the following command:

```
python3 wis2box.ctl.py execute wis2box downloader delete-subscription --topic <topic>
```

This will delete the subscription to the topic you specify and return the JSON object with the current subscriptions.


Managing subscriptions from outside the wis2box
----------------------------------------------

The wis2downloader API-endpoint is proxied on the path `/wis2downloader` on the wis2box host-url, allowing you to interact with it using curl or other HTTP clients from any machine that can reach the wis2box host.

The wis2box-proxy by default secures the path `/wis2downloader` with a bearer token, which can be generated using the `wis2box auth` command as follows:

```
python3 wis2box.ctl.py execute wis2box auth add-token --path wis2downloader -y
```


