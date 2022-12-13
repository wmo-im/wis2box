.. _http-services:

HTTP services
=============

wis2box runs a local 'nginx'-container allowing access to the following HTTP-based services on port 8999:

* wis2box-api: WIS2BOX_URL/oapi
* wis2box-ui: WIS2BOX_URL/
* incoming data: WIS2BOX_URL/wis2box-incoming
* public data: WIS2BOX_URL/data

You can edit docker/nginx/nginx.conf to control which services are exposed through the nginx-container include in your stack.

You can edit docker/docker-compose.override.yml to change the port on which the 'web-proxy'-services exposes HTTP on the local host.

.. note::
    The WIS2-notifications published by the wis2box include the path <wis2box-url>/data/ . 
    This path has to be accessible by the client receiving the WIS2Notification over MQTT, or the data referenced can not be downloaded.

To share your data with the WIS2-network make sure that 'WIS2BOX_URL' defined in dev.env points to the externally accessible url for your HTTP-services. 
After updating this environment-variable please stop & start your wis2box using wis2box-ctl.py and republish your data using the command 'wis2box metadata discovery publish'. 

.. note::
  By default the environment-variable WIS2BOX_URL=http://localhost:8999. 
  This URL will define the /data url used in the canonical link your data in MQTT and the dataset location in your discovery metadata.

wis2box-API
-----------

The wis2box-API uses `pygeoapi`_,  which implements the OGC API standards, to provide programmatic access to the data collections hosted in the backed.

.. image:: screenshots/wis2box_api.png
  :width: 800
  :alt: wis2box-api

.. note::
  
  Currently the default API-backend in the wis2box-stack uses `Elasticsearch`_ .
  A dedicated docker-volume 'es-data' is created on your host when you start your wis2box. 
  As long as this volume is not deleted you can remove/update the containers in the wis2box-stack without losing data.

wis2box-UI
----------

The wis2box-UI uses the wis2box-API to visualize the data configured and shared through your wis2box.

The 'map' or 'explore'-option of each dataset allows you to visualize Weather Observations per station.

.. image:: screenshots/wis2box_map_view.png
  :width: 800
  :alt: wis2box-map-view

.. image:: screenshots/wis2box_data_view.png
  :width: 800
  :alt: wis2box-data-view

.. _`pygeoapi`: https://pygeoapi.io/
.. _`elasticsearch`: https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html