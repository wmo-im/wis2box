.. _station-metadata:

Station metadata
================

wis2box is designed to support data ingest and processing of any kind. For observations,
processing workflow typically requires station metadata to be present at runtime.

wis2box provides the ability to cache station metadata from the `WMO OSCAR/Surface`_ system.

To cache your stations of interest, create a CSV file formatting per below, specifying one
line (with station name and WIGOS station identifier [WSI]) per station:

.. literalinclude:: ../../../tests/data/metadata/station/station_list.csv

Use this CSV to cache station metadata:

.. code-block:: bash

   wis2box metadata station cache /path/to/station_list.csv

Resulting station metadata files (JSON) are stored in ``WIS2BOX_DATADIR/data/metadata/station`` and
can be used by wis2box data processing pipelines. These data are required before starting automated
processing.

Summary
-------

At this point, you have cached the required station metadata for your given dataset(s).

.. _`WMO OSCAR/Surface`: https://oscar.wmo.int/surface
