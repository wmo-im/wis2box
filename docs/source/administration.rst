.. _administration:

Administration
==============

wis2box is designed to be built as a network of virtual machines within a virtual network. Once this
is built, users login into the main wis2box machine to setup their workflow and configurations for
data processing and publishing.

The ``wis2box-ctl.py`` utility provides a number of tools for managing the wis2box containers.

The following steps provide an example of container management workflow.

.. code-block:: bash

   # build all images
   python3 wis2box-ctl.py build

   # start system
   python3 wis2box-ctl.py start

   # stop system
   python3 wis2box-ctl.py stop

   # view status of all deployed containers
   python3 wis2box-ctl.py status


.. note::

    Run ``python3 wis2box-ctl.py --help`` for all usage options.


With wis2box now installed and started, it's time to start up the box and login to the wis2box container:

.. code-block:: bash

    python3 wis2box-ctl.py start
    python3 wis2box-ctl.py login

Now that you are logged into the wis2box container, it's now time to manage station metadata, discovery metadata
and data processing pipelines.

Public environment variables
----------------------------

The following environment variables are used for public services:

- ``WIS2BOX_API_URL``: API application
- ``WIS2BOX_MQTT_URL``: MQTT broker
- ``WIS2BOX_URL``: Web application, including access to data download/object storage

Default service ports
---------------------

A default wis2box installation utilizes the following ports for public services:

Public services
^^^^^^^^^^^^^^^

- ``8999``: Web application, API application, storage
- ``1883``: Message broker


Internal services
^^^^^^^^^^^^^^^^^

- ``1883``: Message broker
- ``9200``: Elasticsearch
- ``9000``: MinIO
- ``9001``: MinIO admin UI

Changing default ports
^^^^^^^^^^^^^^^^^^^^^^

The ``docker/docker-compose.override.yml`` file provides definitions on utilized ports.  To change default
ports, edit ``docker/default.env``  before stopping and starting wis2box for changes to take effect.


MQTT Quality of Service (QoS)
-----------------------------

The `quality of service`_ level of all wis2box powered brokers is always ``1`` by default.


.. _`quality of service`: https://www.hivemq.com/blog/mqtt-essentials-part-6-mqtt-quality-of-service-levels
