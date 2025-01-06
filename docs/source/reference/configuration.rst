.. _configuration:

Configuration
=============

Once you have installed wis2box, it is time to setup the configuration. wis2box setup is based on
a simple configuration that can be adjusted depending the user's needs and deployment environment.

Environment variables
---------------------

wis2box configuration is driven primarily by a set of environment variables. The runtime
configuration is defined in the `Env`_ format in a plain text file named ``wis2box.env``. 
An example is provided in ``wis2box.env.example``.

You can either copy the example-file to ``wis2box.env`` and adjust the values to your needs or run the following command
to create a new ``wis2box.env`` file by answering a few questions on the command line:

.. code-block:: bash

    python3 wis2box-create-config.py

For further / specialized configuration, see the sections below.

``WIS2BOX_HOST_DATADIR``
^^^^^^^^^^^^^^^^^^^^^^^^

The value of ``WIS2BOX_HOST_DATADIR`` maps the wis2box data directory from the host system to the containers.


Sections
--------

.. note::

   A reference configuration can always be found in the wis2box `GitHub`_ repository. The :ref:`quickstart`
   uses a variant of ``wis2box.env.example`` with mappings to the test data, as an example.

wis2box environment variables can be categorized via the following core sections:

- **Storage**: MinIO configuration
- **API**: API configuration for provisioning the OGC API capabilities
- **Logging**: logging configuaration for wis2box
- **Pub/Sub**: Pub/Sub options
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
    WIS2BOX_STORAGE_USERNAME=wis2box  # username for the storage-layer
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
    WIS2BOX_API_URL=http://localhost/pygeoapi  # public landing page endpoint
    WIS2BOX_API_BACKEND_TYPE=Elasticsearch  # backend provider type
    WIS2BOX_API_BACKEND_URL=http://elasticsearch:9200  # internal backend connection URL
    WIS2BOX_DOCKER_API_URL=http://wis2box-api:80/oapi  # container name of API container (for internal communications/workflow)

Logging
^^^^^^^

The logging directives control logging level/severity and output.

.. code-block:: bash

    WIS2BOX_LOGGING_LOGLEVEL=ERROR  # the logging level (see https://docs.python.org/3/library/logging.html#logging-levels)
    WIS2BOX_LOGGING_LOGFILE=stdout  # the full file path to the logfile or ``stdout`` to display on console

Pub/Sub
^^^^^^^

Pub/Sub configuration provides connectivity information for the Pub/Sub broker.

.. code-block:: bash

    WIS2BOX_BROKER_HOST=mosquitto  # the hostname of the internal broker
    WIS2BOX_BROKER_PORT=1883  # the port of the internal broker
    WIS2BOX_BROKER_USERNAME=wis2box  # the username of the internal broker
    WIS2BOX_BROKER_PASSWORD=wis2box  # the password of the internal broker
    WIS2BOX_BROKER_PUBLIC=mqtt://foo:bar@localhost:1883  # RFC 1738 URL of public broker endpoint
    WIS2BOX_BROKER_QUEUE_MAX=1000  # maximum number of messages to hold in the queue per client

.. note::

   ``WIS2BOX_BROKER_QUEUE_MAX`` should be configured according to the setup of wis2box, relative to the number
   of expected observations per day.  See :ref:`getting-started` for more information on system requirements.


Note that the ``WIS2BOX_BROKER_PUBLIC`` URL can be used to publish WIS2 notifications to an external broker. By default, the internal broker is used.

Apart from the wis2box internal user defined by the ``WIS2BOX_BROKER_USERNAME`` and ``WIS2BOX_BROKER_PASSWORD`` environment variables, the wis2box broker will also include the user ``everyone`` with password ``everyone``.

The ``everyone`` user has **read-only** access to the ``origin/#`` topic and can be used to allow the WIS2 Global Broker to subscribe to the wis2box.

To add additional users to the wis2box broker, login to the mosquitto container with the following command:

.. code-block:: bash

    docker exec -it mosquitto /bin/sh

Then, to add a new user, use the following command:

.. code-block:: bash

    mosquitto_passwd -b /mosquitto/config/password.txt <username> <password>

To add or change access rights for mosquitto users, you can edit the file ``/mosquitto/config/acl.conf`` from inside the mosquitto container using the ``vi`` command:

.. code-block:: bash

    vi /mosquitto/config/acl.conf

See the mosquitto documentation for more information on the ACL configuration file.

Restart the mosquitto container for the changes to take effect with the command:

.. code-block:: bash

    docker restart mosquitto

Web application
^^^^^^^^^^^^^^^

Web application configuration provides the ability to customize web components.
All of the below directives are optional.

.. code-block:: bash

    WIS2BOX_BASEMAP_URL="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"  # URL of map tile server to use
    WIS2BOX_BASEMAP_ATTRIBUTION="<a href="https://osm.org/copyright">OpenStreetMap</a> contributors"  # attribution of map tile server
    WIS2BOX_UI_CLUSTER=False # default setting of the cluster toggle
    WIS2BOX_UI_LANG="en" # default language, one of: ar, en, es, fr, ru, zh
    WIS2BOX_UI_LOGO=http://example.com/logo.png # use custom organization logo in the UI
    WIS2BOX_UI_BANNER_COLOR="#014e9e" # use custom background color for header and footer 
    WIS2BOX_UI_DISABLE_SEPARATOR_IMAGE=false # boolean to disable WMO separator

.. note::
    ``WIS2BOX_UI_LOGO`` requires a full URL to the image file.

    If you want to use a local image you can upload your image in the "wis2box-public" bucket of the MinIO storage and use the URL of the image in the configuration.

    Note that the web proxy exposes the "wis2box-public" bucket as the ``/data/`` endpoint.
    If your wis2box uses the URL ``https://wis2box.example.com`` and the uploaded image is named ``logo.png``, 
    you would set ``WIS2BOX_UI_LOGO=https://wis2box.example.com/data/logo.png``.

Other
^^^^^

Additional directives provide various configuration options for the deployment of wis2box.

.. code-block:: bash

    WIS2BOX_URL=http://localhost/  # public wis2box url
    WIS2BOX_AUTH_STORE=http://wis2box-auth # wis2box auth service location


.. note::

   To access internal containers, URL configurations should point to the named containers as specified in ``docker-compose.yml``.


A full configuration example can be found below:

.. literalinclude:: ../../../wis2box.env.example
   :language: bash

Docker Compose
--------------

The Docker Compose setup is driven from the resulting ``wis2box.env`` file created. For advanced cases and/or power users,
updates can also be made to ``docker-compose.yml`` or ``docker-compose.override.yml`` (for changes to ports).

.. _`Env`: https://en.wikipedia.org/wiki/Env
.. _`GitHub`: https://github.com/wmo-im/wis2box/blob/main/default.env
