.. _configuration:

Configuration
=============

Once you have installed wis2box, it is time to setup the configuration. wis2box setup is based on
a simple configuration that can be adjusted depending the user's needs and deployment environment.

Environment variables
---------------------

wis2box configuration is driven primarily by a small set of environment variables. The runtime
configuration is defined in the `Env`_ format in a plain text file named ``dev.env`` and ``docker/default.env``.

Any values set in ``dev.env`` override the default environment variables in ``docker/default.env``. For further / specialized
configuration, see the sections below.

``WIS2BOX_HOST_DATADIR``
^^^^^^^^^^^^^^^^^^^^^^^^

The minimum required setting in ``dev.env`` is the ``WIS2BOX_HOST_DATADIR`` environment variable. Setting this
value is **required** to map the wis2box data directory from the host system to the containers.

It is recommended to set this value to an absolute path on your system.

Sections
--------

.. note::

   A reference configuration can always be found in the wis2box `GitHub`_ repository. The :ref:`quickstart`
   uses a variant of ``wis2box.env`` with mappings to the test data, as an example. For complex installations,
   it is recommended to start configuring wis2box by copying the example ``wis2box.env`` file and modifying
   accordingly.


wis2box environment variables can be categorized via the following core sections:

- **Storage**: MinIO configuration
- **API**: API configuration for provisioning the OGC API capabilities
- **Logging**: logging configuaration for wis2box
- **PubSub**: PubSub options
- **Other**: other miscellaneous options

.. note::

    Configuration directives and reference are described below via annotated examples. Changes in configuration
    require a restart of wis2box to take effect. See the :ref:`administration` section for information on
    managing wis2box.

Storage
^^^^^^^

wis2box currently supports S3 compatible storage (e.g. MinIO, Amazon S3). Additional storage types are planned for
future releases.

The following environment variables can be used to configure `WIS2BOX_STORAGE`.

.. note::

   When using wis2box in production and using the default MinIO-container, please specify a unique ``WIS2BOX_STORAGE_PASSWORD``

.. code-block:: bash

    WIS2BOX_STORAGE_TYPE=S3
    WIS2BOX_STORAGE_SOURCE=http://minio:9000
    WIS2BOX_STORAGE_USERNAME=minio  # username for the storage-layer
    WIS2BOX_STORAGE_PASSWORD=minio123  # password for the storage-layer
    WIS2BOX_STORAGE_INCOMING=wis2box-incoming  # name of the storage-bucket/folder for incoming files
    WIS2BOX_STORAGE_PUBLIC=wis2box-public  # name of the storage-bucket/folder for public files
    WIS2BOX_STORAGE_ARCHIVE=wis2box-archive  # name of the storage-bucket/folder for archived data
    WIS2BOX_STORAGE_DATA_RETENTION_DAYS=7  # number of days to keep files in incoming and public


MinIO
^^^^^

wis2box uses MinIO as the default S3 storage capability.

When overriding the default storage environment variables, please redefine the ``MINIO*`` environment variables to match
your configuration.

.. code-block:: bash

    MINIO_ROOT_USER=${WIS2BOX_STORAGE_USERNAME}
    MINIO_ROOT_PASSWORD=${WIS2BOX_STORAGE_PASSWORD}
    MINIO_NOTIFY_MQTT_USERNAME_WIS2BOX=${WIS2BOX_BROKER_USERNAME}
    MINIO_NOTIFY_MQTT_PASSWORD_WIS2BOX=${WIS2BOX_BROKER_PASSWORD}
    MINIO_NOTIFY_MQTT_BROKER_WIS2BOX=tcp://${WIS2BOX_BROKER_HOST}:${WIS2BOX_BROKER_PORT}


API
^^^

API configurations drive control of the OGC API setup.

.. code-block:: bash

    WIS2BOX_API_TYPE=pygeoapi  # server tpye
    WIS2BOX_API_URL=http://localhost:8999/pygeoapi  # public landing page endpoint
    WIS2BOX_API_BACKEND_TYPE=Elasticsearch  # backend provider type
    WIS2BOX_API_BACKEND_URL=http://elasticsearch:9200  # internal backend connection URL
    WIS2BOX_DOCKER_API_URL  # container name of API container (for internal communications/workflow)

Logging
^^^^^^^

The logging directives control logging level/severity and output.

.. code-block:: bash

    WIS2BOX_LOGGING_LOGLEVEL=ERROR  # the logging level (see https://docs.python.org/3/library/logging.html#logging-levels)
    WIS2BOX_LOGGING_LOGFILE=stdout  # the full file path to the logfile or ``stdout`` to display on console

PubSub
^^^^^^

PubSub configuration provides connectivity information for the PubSub broker.

.. code-block:: bash

    WIS2BOX_BROKER_HOST=mosquitto  # the hostname of the internal broker
    WIS2BOX_BROKER_PORT=1883  # the port of the internal broker
    WIS2BOX_BROKER_USERNAME=wis2box  # the username of the internal broker
    WIS2BOX_BROKER_PASSWORD=wis2box  # the password of the internal broker
    WIS2BOX_BROKER_PUBLIC=mqtt://foo:bar@localhost:1883  # RFC 1738 URL of public broker endpoint


Web application
^^^^^^^^^^^^^^^

Web application configuration provides the ability to customize web components.

.. code-block:: bash

    WIS2BOX_BASEMAP_URL="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"  # URL of map tile server to use
    WIS2BOX_BASEMAP_ATTRIBUTION="<a href="https://osm.org/copyright">OpenStreetMap</a> contributors"  # attribution of map tile server


Other
^^^^^

Additional directives provide various configurationscontrol of configuration options for the deployment of wis2box.

.. code-block:: bash

    WIS2BOX_OSCAR_API_TOKEN=some_token  # OSCAR/Surface API token for OSCAR API interaction
    WIS2BOX_URL=http://localhost:8999/  # public wis2box url
    WIS2BOX_AUTH_STORE=http://wis2box-auth # wis2box auth service location


.. note::

   To access internal containers, URL configurations should point to the named containers as specified in ``docker-compose.yml``.


A full configuration example can be found below:

.. literalinclude:: ../../../examples/config/wis2box.env
   :language: bash

.. literalinclude:: ../../../docker/default.env
   :language: bash

Docker Compose
--------------

The Docker Compose setup is driven from the resulting ``dev.env`` file created. For advanced cases and/or power users,
updates can also be made to ``docker-compose.yml`` or ``docker-compose.override.yml`` (for changes to ports).

.. _`Env`: https://en.wikipedia.org/wiki/Env
.. _`GitHub`: https://github.com/wmo-im/wis2box/blob/main/docker/default.env
