.. _mqtt-configuration:

MQTT configuration
==================

By default, wis2box uses its own internal `Mosquitto`_-container to publish WIS2-notifications. 

To allow the Global Broker to subscribe to WIS2-notifications from your wis2box you have 2 options:

    * enable access to internal broker running in the MQTT-container on your wis2box-host
    * or configure your wis2box to use an external broker

Internal broker
---------------

The internal MQTT broker uses the username=wis2box and password=wis2box. Before opening the MQTT-port for external access we recommend setting a unique password as follows:

.. code-block:: bash

    WIS2BOX_BROKER_USERNAME=wis2box-utopia
    WIS2BOX_BROKER_PASSWORD=myuniquepassword
    WIS2BOX_BROKER_PUBLIC=mqtt://${WIS2BOX_BROKER_USERNAME}:${WIS2BOX_BROKER_PASSWORD}@mosquitto:1883

The internal MQTT broker is accessible on the host=mosquitto with the docker-network used by wis2box. 
By default port 1883 of the mosquitto-container is mapped to port=1883 of the host running wis2box. 
By exposing port 1883 on your host to the Global Broker, the Global Broker can subscribe directly to the internal MQTT-broker on the wis2box.

External broker
---------------

If you do not wish to expose the internal MQTT broker on your wis2box, you can configure your wis2box to publish WIS2-notifications to an external broker by setting the ENV variable 'WIS2BOX_BROKER_PUBLIC'.

.. code-block:: bash

    # For example to use an external broker at host=external.broker.net
    WIS2BOX_BROKER_PUBLIC=mqtts://username:password@external.broker.net:8883  

Sharing data with the global broker
-----------------------------------

The official procedure for a wis2node to start sharing data with the WIS2network is still under development.

During the WIS2 pilot-phase you can contact Rémy from MeteoFrance, who can setup the subscription to your wis2box by the French Global Broker.

.. _`Mosquitto`: https://mosquitto.org/