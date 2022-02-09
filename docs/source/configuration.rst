.. _configuration:

Configuration
=============

Once you have installed wis2box, it is time to setup the configuration. wis2box runtime configuration is defined
in the `Env`_ format in environment file named ``dev.env``.

.. note::

   A reference configuration can always be found in the wis2box `GitHub`_
   repository. The :ref:`quickstart` uses a variant of ``wis2box.env`` with mappings to the test data.

wis2box environment variables can be thought about in the following core sections:

- ``wis2box directories``: directory configuaration for wis2box
- ``wis2box api``: api configuration for wis2box
- ``wis2box logging``: logging configuaration for wis2box
- ``wis2box configuration``: miscellaneous configuration for wis2box
- ``MQP``: MetPX Sarracenia options

Configuration directives and reference are described below via annotated examples. This should reflect any changes made to 
``docker-compose.yml`` and ``docker-compose.override.yml``.

Reference
---------

``wis2box directories``
^^^^^^^^^^^^^^^^^^^^^^^

The `wis2box directories` section provides control of directories on the host machine bound into the docker volume and wis2box. The default relationship
below resembles the directory structure within the wis2box volume.

.. note::

    Make sure to use absolute paths instead of relative paths. ``${PWD}`` provides that functionality in wis2box.env for linux/unix
    based distributions. For users running on windows, replace ``${PWD}`` with the value of the ``cd`` command from the console.

.. code-block:: 

    WIS2BOX_DATADIR=${PWD}/wis2box-data # host directory for wis2box volume
    WIS2BOX_DATA_RETENTION_DAYS=7 # wis2box data retention time

``wis2box api``
^^^^^^^^^^^^^^^

The `wis2box api` section provides control of the Open API for wis2box and the data backend. 

.. code-block::

    WIS2BOX_API_TYPE=pygeoapi # Open API backend
    WIS2BOX_API_URL=http://localhost:8999/pygeoapi # Open API URL
    WIS2BOX_API_CONFIG=${PWD}/docker/pygoeoapi/pygeoapi-config.yml # Open API configuration file
    WIS2BOX_API_BACKEND_TYPE=Elasticsearch # Open API backend provider
    WIS2BOX_API_BACKEND_URL=http://elasticsearch:9200 # Open API backend URL

``wis2box logging``
^^^^^^^^^^^^^^^^^^^

The `wis2box logging` section provides control over wis2box logging.

.. code-block::

    WIS2BOX_LOGGING_LOGLEVEL=ERROR
    WIS2BOX_LOGGING_LOGFILE=stdout

``wis2box configuration``
^^^^^^^^^^^^^^^^^^^^^^^^^

The `wis2box configuration` section provides control of configuration options for the deployment of wis2box.  

.. code-block:: 

    WIS2NODE_OSCAR_API_TOKEN=some_token 
    WIS2NODE_URL=http://localhost:8999/ # wis2node url

``MQP``
^^^^^^^

The ``pub/sub configuration`` section provides control of MetPX Sarracenia configuration options.

.. code-block::

    METPX_SR3_HOST=mosquitto # sarracenia host
    METPX_SR3_BROKER_USERNAME=wis2node # sarracenia broker username
    METPX_SR3_BROKER_PASSWORD=wis2node # sarracenia broker password
    METPX_SR3_EXCHANGE=xs_wis2node_acquisition # sarracenia exchange token

Summary
-------

At this point, you have the configuration ready to start wis2node.

.. _`Env`: https://en.wikipedia.org/wiki/Env
.. _`Github`: https://github.com/wmo-im/wis2node/blob/main/wis2node.env