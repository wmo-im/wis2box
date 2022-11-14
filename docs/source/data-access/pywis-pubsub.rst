.. _pywis-pubsub:

Downloading data from WIS2 using pywis-pubsub
=============================================

Overview
--------

This section provides examples of using the `pywis-pubsub tool <https://github.com/wmo-im/pywis-pubsub>`_ to download data
from WIS2 global services.  WIS2 global services include a Global Broker that
provides users the ability to subscribe to data (via topics) and download to their
local environment / workstation / decision support system from the WIS2 Global Cache.

The pywis-pubsub tool
---------------------

``pywis-pubsub`` is a Python package that provides publish, subscription and download
capability of data from WIS2 infrastructure services.  ``pywis-pubsub`` is included
in both the wis2box and wis2box-subscribe-download containers.

To use ``pywis-pubsub``, run the ``wis2box-subscribe-download`` container as follows:

.. code-block:: bash

   # subscribe by editing/using the configuration in docker/wis2box-subscribe-download/local.yml
   docker-compose -f docker/docker.subscribe-download.yml up


pywis-pubsub requires a configuration in order to run (``docker/wis2box-subscribe-download/local.yml``).  The below YAML provides an example
of a typical configuration:

.. code-block:: yaml

   # fully qualified URL of broker
   broker: mqtts://username:password@host:port

   # whether to run checksum verification when downloading data (default true)
   verify_data: true

   # whether to validate broker messages (default true)
   validate_message: true

   # list of 1..n topics to subscribe to
   topics:
       - '#'

   # storage: filesystem
   storage:
       type: fs
       options:
           path: /tmp/foo/bar

Running pywis-pubsub interactively
----------------------------------

To run pywis-pubsub interactively, pywis-pubsub can be run as follows:

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



Summary
-------

The above examples provide examples of using pywis-pubsub to subscribe and download data from WIS2 global services.
