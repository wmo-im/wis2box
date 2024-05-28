.. _data-ingest-processing-and-publishing:

Data ingest, processing and publishing
======================================

At this point, the system is ready for ingest/processing and publishing.

Data ingest, processing and publishing can be run in automated fashion or via
the wis2box CLI. Data is ingested, processed, and published as WMO BUFR data,
as well as GeoJSON features.

.. warning::
   GeoJSON **data** representations provided in wis2box are in development and
   are subject to change based on evolving requirements for observation data
   representations in WIS2 technical regulations.

Interactive ingest, processing and publishing
---------------------------------------------

The `wis2box` CLI provides a data subsystem to process data interactively. CLI
data ingest/processing/publishing can be run with explicit or implicit topic
hierarchy routing (which needs to be tied to the pipeline via the :ref:`data-mappings`).

Explicit topic hierarchy workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # process a single CSV file
   wis2box data ingest --metadata-id urn:wmo:md:centre-id:mydata -p /path/to/file.csv

   # process a directory of CSV files
   wis2box data ingest --metadata-id urn:wmo:md:centre-id:mydata  -p /path/to/dir

   # process a directory of CSV files recursively
   wis2box data ingest --metadata-id urn:wmo:md:centre-id:mydata -p /path/to/dir -r


Implicit metadata_id workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: bash

   # process incoming data; metadata_id is inferred from fuzzy filepath equivalent
   # wis2box will detect 'mydata' as metadata_id 'urn:md:wmo:mydata'
   wis2box data ingest -p /path/to/foo/bar/baz/data/file.csv


Event driven ingest, processing and publishing
----------------------------------------------

Once all datasets are setup, event driven workflow
will immediately start to listen on files in the ``wis2box-incoming`` storage bucket as they are
placed in the appropriate directory that can be matched to a metadata_id.
