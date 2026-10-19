.. _downloading-data:

Downloading data from WIS2
==========================

.. note::
  
  From wis2box-1.3 the `wis2downloader`_ is no longer included as part of the wis2box-stack.
  The download functionality previously maintained in wis2box will be further developed as part of the `WIS2 Downloader` that runs as a standalone Docker Compose application
  and needs to be installed on an instance separate from the wis2box-stack.

There are different options and tools available to download data from WIS2, including:

 - `pywis-pubsub`_: a python module that provides provides subscription and download capability of data from WIS2
 - `WIS2 Downloader`_: see section below
 - adapting your system to process WIS2 Notification Messages directly

WIS2 Downloader
---------------

WIS2 Downloader provides a scalable system for downloading data from WIS2 Global Brokers and includes a user interface to query the WIS2 Discovery Catalogues to set up subscriptions and manage downloads. 

WIS2 Downloader is a standalone docker compose stack that can be installed on an instance separate from the wis2box instances and enables downloading data from WIS2 Global Services.

For more information see the `WIS2 Downloader documentation`_.

Adapting your system to process WIS2 Notification Messages
-----------------------------------------------------------

To download data from WIS2 it is required to set up a MQTT subscriber loop that subscribes to the topic(s) of interest and parse the message content.

In WIS2 the message content is encoded as per the `WMO WIS2 Notification Message Encoding`_ standard.

A basic example of a MQTT-subscriber-loop in python to extract the URL from the MQTT message and pass it to a client specific function to download the data could look as follows:

.. code-block::

    import json
    import paho.mqtt.client as mqtt_client

    def on_message(client, userdata, message):
      msg_dict = json.load(message.payload.decode('utf-8'))
      for link in msg_dict['links']:
        if link['rel'] == 'canonical' or link['rel'] == 'update':
          client_specific_function(link['href'])

    # Create an MQTT client and connect to the broker
    client = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2, client_id='MyDataClientID')
    client = username_pw_set('everyone', 'everyone')
    client.tls_set(tls_version=2)
    client.connect('globalbroker.meteo.fr', port=8883)
    client.on_message = on_message

    # Subscribe to the topic and start the loop
    client.subscribe('origin/a/wis2/int-ecmwf/data/core/weather/prediction/forecast/cyclone_tracks')
    client.loop_forever()

Small data items may be encoded directly in the MQTT message and can be extracted directly:

.. code-block::

    def on_message(client, userdata, message):
      msg_dict = json.load(message.payload.decode('utf-8'))
      if 'content' in msg_dict and 'value' in msg_dict['content']:
        data = base64.b64decode(msg_dict['content']['value'])
      else:
        # extract URL from links and download data from URL as shown in previous example

Data consumers may also want to apply filters on the message-properties to avoid downloading data that is not relevant for their use case. 
For example the python code to only download data for specific wigos-station-identifiers could look as follows:

.. code-block::

    def on_message(client, userdata, msg):
      msg_dict = json.load(msg.payload.decode('utf-8'))
      wsi = msg_dict['properties'].get('wigos-station-identifier', None)
      if wsi not in my_list_of_relevant_wigos_station_identifiers:
        continue
      else:
        for link in msg_dict['links']:
          if link['rel'] == 'canonical' or link['rel'] == 'update':
            client_specific_function(link['href'])
    
    ...

For more information on the WIS2 Notification Message Standard see the `WMO WIS2 Notification Message Encoding`_ documentation.

.. _`pywis-pubsub`: https://github.com/World-Meteorological-Organization/pywis-pubsub
.. _`WMO WIS2 Notification Message Encoding`: https://wmo-im.github.io/wis2-notification-message/standard/wis2-notification-message-STABLE.html
.. _`WIS2 Downloader`: https://github.com/world-meteorological-organization/wis2downloader
.. _`wis2downloader`: https://github.com/world-meteorological-organization/wis2downloader-v1
.. _`WIS2 Downloader documentation`: https://world-meteorological-organization.github.io/wis2downloader/en/index.html
