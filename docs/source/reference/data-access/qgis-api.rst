.. _qgis-api:

Using QGIS
==========

Overview
--------

This section provides examples of interacting with wis2box API using `QGIS`_.

QGIS is a free and open-source cross-platform desktop GIS application that
supports viewing, editing, and analysis of geospatial data. QGIS supports
numerous format and encoding standards, which enables plug-and-play
interoperability with wis2box data and discovery metadata.

.. image:: /_static/qgis.png
   :scale: 30%
   :alt: QGIS desktop GIS application
   :align: center

Accessing the discovery catalogue
---------------------------------

QGIS provides support for the OGC API - Records standard (discovery). To
interact with the wis2box discovery catalogue:

- from the QGIS menu, select *Web -> MetaSearch -> MetaSearch*
- click the "Services" tab
- click "New"
- enter a name for the discovery catalogue endpoint
- enter the URL to the discovery catalogue endpoint (i.e. ``http://localhost/oapi/collections/discovery-metadata``)
- ensure "Catalogue Type" is set to "OGC API - Records"
- click "OK"

.. image:: /_static/qgis-metasearch-new.png
   :scale: 30%
   :alt: QGIS MetaSearch new connection
   :align: center


This adds the discovery catalogue to the MetaSearch catalogue registry. Click
"Service Info" to display the properties of the discovery catalogue service
metadata.

To search the discovery catalogue, click the "Search" tab, which will provide
the ability to search for metadata records by bounding box and/or full text
search. Click the "Search" button to search the discovery catalogue and
visualize search results. Clicking on metadata records in the search result
table will show footprints on the map to help provide the location of the
search result. Double-clicking a search result will show the entire metadata
record.

.. image:: /_static/qgis-metasearch-search.png
   :scale: 30%
   :alt: QGIS MetaSearch search
   :align: center


.. note::

   For more information on working with catalogues, consult the official
   `QGIS MetaSearch documentation`_.

Visualizing stations
--------------------

QGIS provides support for the OGC API - Features standard (access). To interact
with the wis2box API:

- from the QGIS menu, select *Layer -> Add Layer -> Add WFS Layer...*
- click "New"
- enter a name for the API endpoint
- enter the URL to the API endpoint (i.e. ``http://localhost/oapi``)
- under "WFS Options", set "Version" to "OGC API - Features"
- click "OK"
- click "Connect"

.. image:: /_static/qgis-oafeat-new.png
   :scale: 30%
   :alt: QGIS OGC API - Features new connection
   :align: center


A list of collections is displayed. Select the "Stations" collection and click
"Add".  The Stations collection is now added to the map. To further explore:

- click on the "Identify" (i) and click on a station to display station properties
- select *Layer -> Open Attribute Table* to open all stations in a tabular view

.. image:: /_static/qgis-oafeat-stations.png
   :scale: 30%
   :alt: QGIS OGC API - Features stations
   :align: center


Note that the same QGIS workflow can be executed for any other collection
listed from wis2box API.

.. note::

   For more information on working with OGC API - Features, consult the official
   `QGIS WFS documentation`_.


Summary
-------

The above examples provide a number of ways to utilize the wis2box API from
the QGIS desktop GIS application.


.. _`QGIS`: https://qgis.org
.. _`QGIS MetaSearch documentation`: https://docs.qgis.org/latest/en/docs/user_manual/plugins/core_plugins/plugins_metasearch.html
.. _`QGIS WFS documentation`: https://docs.qgis.org/3.16/en/docs/user_manual/working_with_ogc/ogc_client_support.html#wfs-and-wfs-t-client
