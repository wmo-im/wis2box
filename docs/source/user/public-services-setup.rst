.. _public-services-setup:

Public services setup
=====================

To share your data with the WIS2 network, you need to expose some of your wis2box services to the Global Services:

* The Global Cache needs to be able to access to your HTTP endpoint to download data published by your wis2box instance
* The Global Broker needs to be able to subscribe to your MQTT endpoint to receive WIS2 notifications published by your wis2box instance

Nginx (HTTP)
^^^^^^^^^^^^

wis2box runs a local nginx container allowing access to the following HTTP based services on port 8999:


.. csv-table::
   :header: Function, URL
   :align: left

   API (wis2box-api),`WIS2BOX_URL/oapi`
   UI (wis2box-ui),`WIS2BOX_URL/`
   Storage (incoming data) (minio:wis2box-incoming),`WIS2BOX_URL/wis2box-incoming`
   Storage (public data) (minio:wis2box-public),`WIS2BOX_URL/data`


You can edit ``nginx/nginx.conf`` to control which services are exposed through the nginx-container include in your stack.

You can edit ``docker-compose.override.yml`` to change the port on which the ``web-proxy`` service exposes HTTP on the localhost.

.. note::
    The WIS2 notifications published by the wis2box includes the path ``<wis2box-url>/data/``.
    This path has to be publically accessible by the client receiving the WIS2 notification over MQTT, or the data referenced cannot be downloaded

To share your data with the WIS2 network, ensure that ``WIS2BOX_URL`` as defined in ``dev.env`` points to the externally accessible URL for your HTTP services. 

After updating ``WIS2BOX_URL``, please stop and start your wis2box using ``wis2box-ctl.py`` and republish your data using the command ``wis2box metadata discovery publish``.

.. note::

   By default the environment variable ``WIS2BOX_URL`` resolves to ``http://localhost:8999``.
   This URL will define the ``/data`` URL used in the canonical link as part of your data in MQTT, as well as the dataset location in your discovery metadata.

wis2box API
-----------

The wis2box API uses `pygeoapi`_,  which implements the `OGC API`_ suite of standards, to provide programmatic access to the data collections hosted in your wis2box.

.. image:: ../_static/wis2box-api.png
  :width: 800
  :alt: wis2box API-api

.. note::
  
  Currently, the default API backend in the wis2box stack uses `Elasticsearch`_.
  A dedicated Docker-volume ``es-data`` is created on your host when you start your wis2box. 
  As long as this volume is not deleted you can remove/update the containers in the wis2box stack without losing data.

wis2box user interface
----------------------

The wis2box user interface uses the wis2box API to visualize the data configured and shared through your wis2box.

The 'map' or 'explore' option of each dataset allows you to visualize Weather Observations per station.

.. image:: ../_static/wis2box-map-view.png
  :width: 800
  :alt: wis2box UI map visualization

.. image:: ../_static/wis2box-data-view.png
  :width: 800
  :alt: wis2box UI data graph visualization

Mosquitto (MQTT)
^^^^^^^^^^^^^^^^

By default, wis2box uses its own internal `Mosquitto`_ container to publish WIS2 notifications. 

To allow the WIS2 Global Broker to subscribe to WIS2 notifications from your wis2box you have 2 options:

    * enable access to internal broker running in the MQTT container on your wis2box host
    * configure your wis2box to use an external broker

Internal broker
---------------

The internal MQTT broker uses the username ``wis2box`` and password ``wis2box``.  Before opening the MQTT port for external access, it is recommended to set a unique password as follows:

.. code-block:: bash

    WIS2BOX_BROKER_USERNAME=wis2box-utopia
    WIS2BOX_BROKER_PASSWORD=myuniquepassword
    WIS2BOX_BROKER_PUBLIC=mqtt://${WIS2BOX_BROKER_USERNAME}:${WIS2BOX_BROKER_PASSWORD}@mosquitto:1883

The internal MQTT broker is accessible on the host ``mosquitto`` within the Docker network used by wis2box.

By default port 1883 of the mosquitto-container is mapped to port 1883 of the host running wis2box. 

By exposing port 1883 on your host, the Global Broker can subscribe directly to the internal MQTT broker on the wis2box.

External broker
---------------

If you do not wish to expose the internal MQTT broker on your wis2box, you can configure your wis2box to publish WIS2 notifications to an external broker by setting the environment variable ``WIS2BOX_BROKER_PUBLIC``.

.. code-block:: bash

    # For example to use an external broker at host=external.broker.net
    WIS2BOX_BROKER_PUBLIC=mqtts://username:password@external.broker.net:8883  

Sharing data with the WIS2 Global Broker
----------------------------------------

The official procedure for a WIS2 Node to share data with the WIS2 network is currently in development.  Contact wis at wmo.int for more information on connectivity with the WIS2 network.

Next: :ref:`downloading-data`


.. _`Mosquitto`: https://mosquitto.org/
.. _`pygeoapi`: https://pygeoapi.io/
.. _`Elasticsearch`: https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html
.. _`OGC API`: https://ogcapi.ogc.org
