.. _data-ingest-processing-and-publishing:

Data ingest, processing and publishing
======================================

At this point, the system is ready for ingest/processing and publishing.

Data ingest, processing and publishing can be run in automated fashion or via
the wis2box CLI. Data is ingested, processed, and published  as WMO BUFR data,
as well GeoJSON features.

Interactive ingest, processing and publishing
---------------------------------------------

The `wis2box` CLI provides a data subsystem to process data interactively. CLI
data ingest/processing/publishing can be run with explicit or implicit topic
hierarchy routing (which needs to be tied to the pipeline via the :ref:`data-mappings`).

Explicit topic hierarchy workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # process a single CSV file
   wis2box data ingest --topic-hierarchy foo.bar.baz -p /path/to/file.csv

   # process a directory of CSV files
   wis2box data ingest --topic-hierarchy foo.bar.baz -p /path/to/dir

   # process a directory of CSV files recursively
   wis2box data ingest --topic-hierarchy foo.bar.baz -p /path/to/dir -r


Implicit topic hierarchy workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # process incoming data; topic hierarchy is inferred from fuzzy filepath equivalent
   # wis2box will detect 'foo/bar/baz' as topic hierarchy 'foo.bar.baz'
   wis2box data ingest -p /path/to/foo/bar/baz/data/file.csv


Event driven ingest, processing and publishing
----------------------------------------------

One all metadata, topic hierarchies, and data configurations are setup, event driven workflow
will immediately start to listen on files in ``WIS2BOX_DATADIR/data/incoming`` as they are
placed in the appropriate topic hierarchy directory.

.. note::

    wis2box can make ``WIS2BOX/data/incoming`` accessible via webdav by enabling ``docker/docker-compose.webdav.yml``.


Summary
-------

Congratulations! At this point, you have successfully setup a wis2box data pipeline. Data should be flowing through
the system.
