.. _configuration:

Configuration
=============

Once you have installed wis2node, it is time to setup the configuration. wis2node runtime configuration is defined
in the `Env <https://en.wikipedia.org/wiki/Env>`_ format in environment file named ``dev.env``.

.. note::

   A reference configuration can always be found in the wis2node `GitHub <https://github.com/wmo-im/wis2node/blob/main/wis2node.env>`_
   repository. The :ref:`quickstart` uses a variant of ``wis2node.env`` with mappings to the test data.

wis2node environment variables can be thought about in the following core sections:

- ``wis2node directories``: directories to mount in the wis2node docker volume
- ``wis2node configuration``: configuration options for wis2node
- ``pub/sub configuration``: MetPX Sarracenia options

Configuration directives and reference are described below via annotated examples.

Reference
---------

``wis2node directories``
^^^^^^^^^^^^^^^^^^^^^^^^

The `wis2node directories` section provides control of directories on the host machine bound into the docker volume and wis2node. The default relationship
below resembles the directory structure within the wis2node volume. Should the directory structure outside the docker volume not resemble the wis2node data directory, 
subdirectories can be mapped from the host system into the wis2node volume

.. code-block:: 

    WIS2NODE_DATADIR=${PWD}/wis2node-data # host directory for wis2node volume

    WIS2NODE_DATADIR_CONFIG=$WIS2NODE_DATADIR/data/config # Config folder mapping to wis2node volume
    WIS2NODE_DATADIR_INCOMING=$WIS2NODE_DATADIR/data/incoming # Incoming folder mapping to wis2node volume
    WIS2NODE_DATADIR_OUTGOING=$WIS2NODE_DATADIR/data/outgoing # Outgoing folder mapping to wis2node volume
    WIS2NODE_DATADIR_PUBLIC=$WIS2NODE_DATADIR/data/public # Public folder mapping  to wis2node volume

``wis2node configuration``
^^^^^^^^^^^^^^^^^^^^^^^^^^

The `wis2node configuration` section provides control of configuration options for the deployment of wis2node. This should reflect any changes made to 
`docker-compose.yml` and `docker-compose.override.yml`. 

.. code-block:: 

    WIS2NODE_OSCAR_API_TOKEN=some_token 
    WIS2NODE_URL=http://localhost:8999/ # wis2node url
    WIS2NODE_MQP_URL=http://localhost:1883 # wis2node pub/sub url
    WIS2NODE_API_URL=http://localhost:8999/pygeoapi # wis2node open api url
    WIS2NODE_API_CONFIG=${PWD}/docker/pygeoapi/pygeoapi-config.yml # wis2node open api configuration
    WIS2NODE_API_BACKEND_TYPE=Elasticsearch # wis2node api backend
    WIS2NODE_API_BACKEND_HOST=elasticsearch # wis2node api backend hostname
    WIS2NODE_API_BACKEND_PORT=9200 # wis2node api backend port
    WIS2NODE_API_BACKEND_USERNAME=wis2node # wis2node api backend username
    WIS2NODE_API_BACKEND_PASSWORD=wis2node # wis2node api backend password
    WIS2NODE_LOGGING_LOGLEVEL=ERROR # wis2node logging level
    WIS2NODE_LOGGING_LOGFILE=stdout # wisn2ode logging location

``pub/sub configuration``
^^^^^^^^^^^^^^^^^^^^^^^^^

The `pub/sub configuration` section provides control of MetPX Sarracenia configuration options.

.. code-block::

    METPX_SR3_HOST=mosquitto # sarracenia host
    METPX_SR3_BROKER_USERNAME=wis2node # sarracenia broker username
    METPX_SR3_BROKER_PASSWORD=wis2node # sarracenia broker password
    METPX_SR3_EXCHANGE=xs_wis2node_acquisition # sarracenia exchange token

Summary
-------

At this point, you have the configuration ready to start wis2node.
