.. _introduction:

Introduction
============

This is a user guide for publishing and downloading data through the `WIS2`_ network using the wis2box software.

wis2box provides a set of services to help you ingest, transform and publish your weather/climate/water data. 

wis2box implements the core WIS2 requirements of a WIS2 Node:

* Module to produce WIS2 compliant notifications
* MQTT broker
* HTTP endpoint to enable data download

Additional services included in wis2box:

* Customizable plugins to transform input data: default plugins for synop2bufr, csv2bufr and bufr2geojson
* API using `pygeoapi`_ : to enable interaction with the wis2box-backend and exposing data in GeoJSON 
* Web application to enable configuration of station metadata and posting SYNOP and CSV data
* Monitoring functions using `Prometheus`_ and `Grafana`_
* Data visualization through the wis2box user interface

Next: :ref:`getting-started`.

.. _`WIS2`: https://community.wmo.int/activity-areas/wis/wis2-implementation
.. _`pygeoapi`: https://pygeoapi.io
.. _`Prometheus`: https://prometheus.io/docs/introduction/overview
.. _`Grafana`: https://grafana.com/docs/grafana/latest/introduction
