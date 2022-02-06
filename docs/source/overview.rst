.. _overview:

Overview
========

wis2node is a Python reference implementation of a WMO WIS 2.0 node. The project provides a
plug and play toolset to ingest, process, and publish weather/climate/water data using
standards-based approaches in alignment with the `WIS 2.0 principles`_. In addition, wis2node
also provides a access to all data in the WIS 2.0 infrastructure from other wis2nodes and
global centres.

wis2node is designed to have a low barrier to entry for data providers, providing enabling
infrastructure and services for data discovery, access, and visualization.

.. image:: /_static/wis2node-features.jpg
   :scale: 50%
   :alt: wis2node features
   :align: center

Features
--------

* WIS 2.0 compliant: easily register your wis2node with WIS 2.0 infrastructure
* event driven data ingest/process/publishing pipeline
* standards-based data services and access mechanisms

  * `OGC API`_
  * `MQTT`_
* robust and extensible plugin framework


.. _`WIS 2.0 principles`: https://community.wmo.int/activity-areas/wis/wis2-implementation
.. _`WMO`: https://public.wmo.int
.. _`OGC API`: https://ogcapi.org
.. _`MQTT`: https://mqtt.org
