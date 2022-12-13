.. _introduction:

Introduction
============

This is an administrator guide for onboarding your data onto the `WIS 2.0`_ network using the WIS2-in-a-box software.

The "wis2box"-software provides a set of services to help you ingest, transform and publish your weather data. 

Core WIS2 services:

* Module to produce WIS2-compliant notifications
* MQTT-broker
* HTTP-endpoint to enable data download

Additional services:

* Customizable plugins to transform input data
* API exposing data in geojson-format using `pygeoapi`_
* Monitoring functions using `Prometheus`_ and `Grafana`_
* Data visualization through the wis2box-UI

Next: :ref:`gettingstarted`.

.. _`WIS 2.0`: https://community.wmo.int/activity-areas/wis/wis2-implementation
.. _`pygeoapi`: https://pygeoapi.io/
.. _`Prometheus`: https://prometheus.io/docs/introduction/overview/
.. _`Grafana`: https://grafana.com/docs/grafana/latest/introduction/