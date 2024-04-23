.. _public-services-setup:

Public services setup
=====================

To share your data with the WIS2 network, you need to expose some of the wis2box services to the Global Services:

* The Global Cache needs to be able to access to your HTTP endpoint at port 80 to download data published by the wis2box instance
* The Global Broker needs to be able to subscribe to your MQTT endpoint at port 1883 to receive WIS2 notifications published by the wis2box instance

Nginx (HTTP)
^^^^^^^^^^^^

wis2box runs a local nginx container allowing access to the following HTTP based services on port 80:

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
    The canonical link referenced in WIS2 notification messages by your wis2box will use the basepath ``WIS2BOX_URL/data``.
    This path has to be publicly accessible by the client receiving the WIS2 notifications, or the data referenced cannot be downloaded

To share your data with the WIS2 network, ensure that ``WIS2BOX_URL`` as defined in ``wis2box.env`` points to the externally accessible URL for your HTTP services. 

After updating ``WIS2BOX_URL``, please stop and start wis2box using ``wis2box-ctl.py`` and republish your data using the command ``wis2box metadata discovery republish``:

.. code-block:: bash

  python3 wis2box-ctl.py stop
  python3 wis2box-ctl.py start
  python3 wis2box-ctl.py login
  wis2box metadata discovery republish

wis2box API
-----------

The wis2box API uses `pygeoapi`_,  which implements the `OGC API`_ suite of standards, to provide programmatic access to the data collections hosted in wis2box.

.. image:: ../_static/wis2box-api.png
  :width: 800
  :alt: wis2box API-api

.. note::
  
  Currently, the default API backend in wis2box uses `Elasticsearch`_.
  A dedicated Docker volume ``es-data`` is created on your host when you start wis2box. 
  As long as this volume is not deleted you can remove/update the containers in wis2box without losing data.

wis2box user interface
----------------------

The wis2box user interface uses the wis2box API to visualize the data configured and shared through wis2box.

The 'MAP' or 'EXPLORE' option of each dataset allows you to visualize Weather Observations per station.

.. image:: ../_static/wis2box-map-view.png
  :width: 800
  :alt: wis2box UI map visualization

.. image:: ../_static/wis2box-data-view.png
  :width: 800
  :alt: wis2box UI data graph visualization

Mosquitto (MQTT)
^^^^^^^^^^^^^^^^

By default, wis2box uses its own internal `Mosquitto`_ container to publish WIS2 notifications. 

To allow the WIS2 Global Broker to subscribe to WIS2 notifications from wis2box you have 2 options:

    * enable access to internal broker running in the MQTT container on wis2box host
    * configure wis2box to use an external broker

Internal broker
---------------

The internal MQTT broker is accessible on the host ``mosquitto`` within the Docker network used by wis2box.

By default port 1883 of the mosquitto container is mapped to port 1883 of the host running wis2box. 

By exposing port 1883 on your host, the Global Broker will be able to subscribe directly to the internal MQTT broker on wis2box.

.. note::

   The ``everyone`` user is defined by default for public readonly access (``origin/#``) as per WIS2 Node requirements.

External broker
---------------

If you do not wish to expose the internal MQTT broker on wis2box, you can configure wis2box to publish WIS2 notifications to an external broker by setting the environment variable ``WIS2BOX_BROKER_PUBLIC``.

.. code-block:: bash

    # For example to use an external broker at host=example.org
    WIS2BOX_BROKER_PUBLIC=mqtts://username:password@example.org:8883  

.. note::

   The ``everyone`` user is defined by default for public readonly access (``origin/#``) as per WIS2 Node requirements.

SSL
^^^

In order to ensure the security of your data, it is recommended to enable SSL on your wis2box instance.

There are multiple ways to expose the wis2box services over SSL:

- using a reverse proxy (recommended)
- using the built-in SSL support in the ``wis2box-ctl.py`` script

The recommended way to expose the wis2box services over SSL is to use a reverse proxy such as `nginx`_ or `traefik`_. Discuss with your IT team to determine which reverse proxy is best suited for your environment.

Please remember to update the ``WIS2BOX_URL`` and ``WIS2BOX_API_URL`` environment variable after enabling SSL, ensuring your URL starts with ``https://``.

Please note that after changing the ``WIS2BOX_URL`` and ``WIS2BOX_API_URL`` environment variables, you will need to restart wis2box:

.. code-block:: bash

  python3 wis2box-ctl.py stop
  python3 wis2box-ctl.py start

After restarting wis2box, repeat the commands for adding your dataset and publishing your metadata, to ensure that URLs are updated accordingly:

.. code-block:: bash

  python3 wis2box-ctl.py login
  wis2box dataset publish /data/wis2box/metadata/discovery/metadata-synop.yml

Built-in SSL support
--------------------

You can also enable HTTPS and MQTTS directly in the nginx and mosquitto containers running in wis2box.
In this case, the certificate and private key must be available on the host running wis2box

The location of your SSL certificate and private key are defined by the environment variables ``WIS2BOX_SSL_CERT`` and ``WIS2BOX_SSL_KEY`` respectively.

.. code-block:: bash

  WIS2BOX_SSL_CERT=/etc/letsencrypt/live/example.wis2box.io/fullchain.pem
  WIS2BOX_SSL_KEY=/etc/letsencrypt/live/example.wis2box.io/privkey.pem

Please remember to update the ``WIS2BOX_URL`` and ``WIS2BOX_API_URL`` environment variable after enabling SSL, ensuring your URL starts with ``https://``.

You will need to restart your wis2box instance after enabling SSL:

.. code-block:: bash

  python3 wis2box-ctl.py stop
  python3 wis2box-ctl.py start

Your wis2box instance will now apply TLS encryption to the HTTP and MQTT services, exposing them on HTTPS (port 443) and MQTTS (port 8883). 
When setting up the network routing of your wis2box instance, only ports 443 and 8883 need to be exposed to the public internet.

After restarting wis2box, repeat the commands for adding your dataset and publishing your metadata, to ensure that URLs are updated accordingly:

.. code-block:: bash

  python3 wis2box-ctl.py login
  wis2box data add-collection ${WIS2BOX_HOST_DATADIR}/surface-weather-observations.yml
  wis2box metadata discovery publish ${WIS2BOX_HOST_DATADIR}/surface-weather-observations.yml

Registering your WIS2 Node
--------------------------

Contact wis2-support@wmo.int for the procedure to register your WIS2 Node with the WIS2 network.

Next: :ref:`downloading-data`

.. _`Mosquitto`: https://mosquitto.org/
.. _`pygeoapi`: https://pygeoapi.io/
.. _`Elasticsearch`: https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html
.. _`OGC API`: https://ogcapi.ogc.org
.. _`nginx`: https://www.nginx.com/
.. _`traefik`: https://traefik.io/
