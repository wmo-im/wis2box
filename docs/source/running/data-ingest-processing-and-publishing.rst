.. _data-ingest-processing-and-publishing:

Data ingest, processing and publishing
======================================

Setup Data Processing
---------------------

..
    TODO: Setup data processing

Data processing is based on topic hierarchies.


Publish API collection
----------------------

..
    TODO: Publish API collection

Data ingest
-----------

.. 
    TODO: Data injest

Data can be processed by wis2box via command line interface or an event driven workflow.

CLI
^^^

Event
^^^^^

The event driven workflow watches and processes files as they are placed in the appropriate topic hierarchy
based subdirectory of `WIS2NODE_DATADIR_INCOMING`.

.. note::

    wis2box can make `WIS2NODE_DATADIR_INCOMING` accessible via webdav by adding `docker-compose.webdav.yml`.

Summary
-------

..
    TODO: Summary
