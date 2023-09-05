.. _station-metadata:

Station metadata
================

wis2box is designed to support data ingest and processing of any kind. For observations,
processing workflow typically requires station metadata to be present at runtime.

To manage your stations of interest, create a CSV file named ``metadata/station/station_list.csv`` in ``$WIS2BOX_HOST_DATADIR``,
specifying one line per station as follows:

.. literalinclude:: ../../../../examples/config/station_list.csv

This CSV file is used by wis2box data processing pipelines and is required before starting automated
processing.

.. note:: run the command ``wis2box metadata station publish-collection`` to
          publish your stations as a collection to the wis2box API


.. seealso:: :ref:`api-publishing`

OSCAR/Surface
-------------

wis2box can derive station information from `OSCAR/Surface`_.  To verify station metadata from OSCAR/Surface:

.. code-block:: bash

   wis2box metadata station WSI


where ``WSI`` is the WIGOS Station Identifier.  This command will return the information required in the
station list for wis2box data processing and publication.  To add the station information to the station list,
copy and paste the output of the above command, or rerun the above command, writing to the station list
automatically:


.. code-block:: bash

   wis2box metadata station WSI >> ~/wis2box-data/metadata/station/station_list.csv


Summary
-------

At this point, you have cached the required station metadata for your given dataset(s).

.. _`OSCAR/Surface`: https://oscar.wmo.int/surface
