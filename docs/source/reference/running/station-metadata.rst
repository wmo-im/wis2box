.. _station-metadata:

Station metadata
================

`OSCAR/Surface`_ is the key resource for station metadata and contains a global compilation of the metadata for stations
that exchange data internationally.
Prior to exchanging data on WIS2, stations must be registered in OSCAR/Surface and assigned a WIGOS station identifier (WSI).

The wis2box API can be used to retrieve station metadata from OSCAR/Surface and cache a subset of the station metadata in the wis2box backend.

The station metadata can be cached in two ways:

* from the command-line in the wis2box-management container, after populating the station list CSV file
* from the station editor in the wis2box-webapp, available at ``$WIS2BOX_URL/wis2box-webapp/station``

The plugins for converting data to BUFR will use the cached station metadata as follows:

* synop2bufr: The station metadata is used to derives the WSI by matching with the traditional station identifier in the FM-12 input data. The station metadata is also used to encode the location and barometer height above sea-level into the BUFR message
* csv2bufr: The station metadata list is used to whitelist records to publish. If no match is found in the station list for an input record based on the WSI, the record is not published
* bufr2bufr: If the WSI is missing in the input BUFR data, the WSI is looked up in the station metadata list using the traditional station identifier (block and station number, ship callsign etc.) and inserted into the BUFR message. Similarly, if the location or station elevation are missing in the input BUFR data, these are looked up in the station metadata list and inserted into the BUFR message as required before further processing

Using the station editor in the wis2box-webapp
----------------------------------------------

When using the station editor in the wis2box-webapp, if a WIGOS Station Identifier (WSI) is provided, the associated station metadata will be populated from OSCAR/Surface.

After the data has been fetched you can populate any missing fields and associate the station with one or more topics.

Using the command-line
----------------------

To cache station metadata from the command-line, edit the CSV file named ``metadata/station/station_list.csv`` in ``$WIS2BOX_HOST_DATADIR``,
specifying one line per station as follows:

.. literalinclude:: ../../../../examples/config/station_list.csv

Then login in to the wis2box-container and run the command ``wis2box metadata station publish-collection``
to insert all stations in the station list into the backend.

Within the wis2box-container you can fetch the required station metadata from OSCAR/Surface using the following command:

.. code-block:: bash

   wis2box metadata station get WSI

where ``WSI`` is the WIGOS Station Identifier.  This command will return the information required in the
station list for wis2box data processing and publication.  To add the station information to the station list,
copy and paste the output of the above command, or rerun the above command, writing to the station list
file as follows:

.. code-block:: bash

   wis2box metadata station get WSI >> ~/wis2box-data/metadata/station/station_list.csv

After using the command-line to cache the station metadata, you will need to associate the stations with one or more topics to visualize the stations in the wis2box-ui.

To associate all stations in your station metadata to one topic, you can use the following command:

.. code-block:: bash

   wis2box metadata station add-topic <topic-id>

To add a topic to a single station, you can use the following command:

.. code-block:: bash

   python3 wis2box-ctl.py login
   wis2box metadata station add-topic --wsi <station-id> <topic-id>

To add a topic to all stations from a specific territory, for example Italy, you can use the following command:

.. code-block:: bash

   python3 wis2box-ctl.py login
   wis2box metadata station add-topic --territory-name Italy <topic-id>

Summary
-------

At this point, you have cached the required station metadata for your given dataset(s).

.. _`OSCAR/Surface`: https://oscar.wmo.int/surface
