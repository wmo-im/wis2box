.. _services:

Services
========

wis2box provides a number of data access services and mechanisms in providing data
to users, applications and beyond.

OGC API
-------

wis2box data and metadata are made available via the `OGC API - Features`_ and `OGC API - Records`_
standards.

The OGC API endpoint is located by default at http://localhost:8999/pygeoapi

TODO: example requests

SpatioTemporal Asset Catalog (STAC)
-----------------------------------

The wis2box `SpatioTemporal Asset Catalog (STAC)`_ endpoint can be found at:

http://localhost:8999/stac

...providing the user with a crawlable catalogue of all data on a wis2box.


Web Accessible Folder (WAF)
----------------------------

The wis2box `SpatioTemporal Asset Catalog (STAC)`_ endpoint can be found at:

http://localhost:8999/data/

...providing the user with a crawlable online folder of all data on a wis2box.

MQTT
----

The wis2box `MQTT`_ endpoint can be found at:

mqtt://localhost:1883

...providing a PubSub capability for event driven subscription and access.


.. _`OGC API - Features`: https://ogcapi.ogc.org/features
.. _`OGC API - Records`: https://ogcapi.ogc.org/records
.. _`SpatioTemporal Asset Catalog (STAC)`: https://stacspec.org
.. _`MQTT`: https://mqtt.org
