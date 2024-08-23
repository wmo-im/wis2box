.. _services:

Services
========

wis2box provides a number of data access services and mechanisms in providing data
to users, applications and beyond.

Discovery Catalogue
-------------------

The discovery catalogue is powered by `OGC API - Records`_ and is located at http://localhost/oapi/collections/discovery-metadata

The OGC API endpoint is located by default at http://localhost/oapi.  The discovery catalogue endpoint is located at http://localhost/oapi/collections/discovery-metadata

Below are some examples of working with the discovery catalogue.

- description of catalogue: http://localhost/oapi/collections/discovery-metadata
- catalogue queryables: http://localhost/oapi/collections/discovery-metadata/queryables
- catalogue queries

  - records (browse): http://localhost/oapi/collections/discovery-metadata/items
  - query by spatial (bounding box): http://localhost/oapi/collections/discovery-metadata/items?bbox=32,-17,36,-8
  - query by temporal extent (since): http://localhost/oapi/collections/discovery-metadata/items?datetime=2021/..
  - query by temporal extent (before): http://localhost/oapi/collections/discovery-metadata/items?datetime=../2022
  - query by freetext: http://localhost/oapi/collections/discovery-metadata/items?q=observations

.. note::

   - adding ``f=json`` to URLs will provide the equivalent JSON/GeoJSON representations
   - query predicates (``datetime``, ``bbox``, ``q``, etc.) can be combined

.. seealso:: :ref:`data-access`


Data API
--------

wis2box data is made available via `OGC API - Features`_ and is located at http://localhost/oapi
standards.

The OGC API endpoint is located by default at http://localhost/oapi

Below are some examples of working with the discovery catalogue.

.. note::

   - the examples below use the ``urn:wmo:md:mw-mw_met_centre-test:surface-weather-observations`` collection as described
     in the :ref:`quickstart`.  For other dataset collections, use the same query patterns below, substituting the
     collection id accordingly


- list of dataset collections: http://localhost/oapi/collections
- collection description: http://localhost/oapi/collections/urn:wmo:md:mw-mw_met_centre-test:surface-weather-observations
- collection queryables: http://localhost/oapi/collections/urn:wmo:md:mw-mw_met_centre-test:surface-weather-observations/queryables
- collection items (browse): http://localhost/oapi/collections/urn:wmo:md:mw-mw_met_centre-test:surface-weather-observations/items
- collection queries

  - set limit/offset (paging): http://localhost/oapi/collections/urn:wmo:md:mw-mw_met_centre-test:surface-weather-observations/items?limit=1&startindex=2
  - query by spatial (bounding box): http://localhost/oapi/collections/urn:wmo:md:mw-mw_met_centre-test:surface-weather-observations/items?bbox=32,-17,36,-8
  - query by temporal extent (since): http://localhost/oapi/collections/urn:wmo:md:mw-mw_met_centre-test:surface-weather-observations/items?datetime=2021/..
  - query by temporal extent (before): http://localhost/oapi/collections/urn:wmo:md:mw-mw_met_centre-test:surface-weather-observations/items?datetime=../2022

.. note::

   - adding ``f=json`` to URLs will provide the equivalent JSON/GeoJSON representations
   - query predicates (``datetime``, ``bbox``, ``q``, etc.) can be combined

.. seealso:: :ref:`data-access`


Management API
^^^^^^^^^^^^^^

The Data API also provides a management API to manage resources in alignment with `OGC API - Features - Part 4: Create, Replace, Update and Delete`_, which is available at http://localhost/oapi/admin.


SpatioTemporal Asset Catalog (STAC)
-----------------------------------

The wis2box `SpatioTemporal Asset Catalog (STAC)`_ endpoint can be found at:

http://localhost/stac

...providing the user with a crawlable catalogue of all data on a wis2box.


Web Accessible Folder (WAF)
----------------------------

The wis2box Web Accessible Folder publich bucket endpoint can be found at:

http://localhost/data/

...providing the user with a crawlable online folder of all data on a wis2box.


Broker
------

The wis2box broker is powered by `MQTT`_ and can be found at:

mqtt://everyone:everyone@localhost:1883

mqtt://localhost:1883

...providing a Pub/Sub capability for event driven subscription and access.

.. note::

   The ``everyone`` user is defined by default for public readonly access (``origin/#``) as per WIS2 Node requirements.

Adding services
---------------

wis2box's architecture allows for additional services as required by
adding Docker containers. Examples of additional services include adding a container
for a samba share or FTP server. Key considerations for adding services:

- Storage buckets can be found at http://minio:9000
- Elasticsearch indexes can be found at the container/URL ``http://elasticsearch:9200``


.. _`OGC API - Features`: https://ogcapi.ogc.org/features
.. _`OGC API - Records`: https://ogcapi.ogc.org/records
.. _`SpatioTemporal Asset Catalog (STAC)`: https://stacspec.org
.. _`MQTT`: https://mqtt.org
.. _`OGC API - Features - Part 4: Create, Replace, Update and Delete`: https://docs.ogc.org/DRAFTS/20-002.html
