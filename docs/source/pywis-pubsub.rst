.. _pywis-pubsub:

Downloading data from WIS2 using pywis-pubsub
=============================================

Overview
--------

This section provides guidance how to download data from WIS2 global services. 
WIS2 global services include a Global Broker that provides users the ability to subscribe to data (via topics) and download to their
local environment / workstation / decision support system from the WIS2 Global Cache.

The pywis-pubsub tool
---------------------

WIS2-in-a-box can help you subscribe and download data from the WIS2 network, by using the wis2box-subscribe-download container, inside of which runs the `pywis-pubsub tool <https://github.com/wmo-im/pywis-pubsub>`_

``pywis-pubsub`` is a Python package that provides publish, subscription and download capability of data from WIS2 infrastructure services.  

Before starting the wis2box-subscribe-download container,  the default configuration (provided in ``docker/wis2box-subscribe-download/local.yml``)
must be updated, by defining the URL of the MQTT broker as well as the desired topics to subscribe to.

In addition, the storage path should be updated to specify where the downloaded should be saved to.

.. code-block:: yaml

   # fully qualified URL of broker
   broker: mqtts://username:password@host:port

   # whether to run checksum verification when downloading data (default true)
   verify_data: true

   # whether to validate broker messages (default true)
   validate_message: true

   # list of 1..n topics to subscribe to
   topics:
       - 'cache/a/wis2/topic1/#'
       - 'cache/a/wis2/topic2/#'

   # storage: filesystem
   storage:
       type: fs
       options:
           path: /tmp/foo/bar

To start a continuous subscribe-and-download process, run the ``wis2box-subscribe-download`` container as follows (``-d`` for detached mode, ``--build`` to ensure changes in local.yml are built into the container):

.. code-block:: bash

   docker-compose -f docker/docker.subscribe-download.yml up -d --build

To stop the subscribe-and-download process, run the following command:

.. code-block:: bash

   docker-compose -f docker/docker.subscribe-download.yml down


Running pywis-pubsub interactively
----------------------------------

pywis-pubsub can also be run interactively from inside the wis2box main container as follows:

.. code-block:: bash

   # login to wis2box main container
   python3 wis2box-ctl.py login

   # edit a local configuration by using docker/wis2box-subscribe-download/local.yml as a template
   vi /data/wis2box/local.yml

   # connect, and simply display data notifications
   pywis-pubsub subscribe --config local.yml

   # connect, and additionally download messages
   pywis-pubsub subscribe --config local.yml --download

   # connect, and filter messages by bounding box geometry
   pywis-pubsub subscribe --config local.yml --bbox=-142,42,-52,84
