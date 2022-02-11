.. _data-retention:


Data retention
==============

wis2box is configured to set data retention according to your requirements. Data retention is managed
via the ``WIS2NODE_DATA_RETENTION_DAYS`` environment variable as part of configuring wis2box.  Data
retention includes cleaning of published data and archiving of incoming/raw data.

Cleaning
--------

Cleaning is performed by default daily at 0Z by the system, and can also be run interactively with:


.. code-block:: bash

   # delete data older than WIS2NODE_DATA_RETENTION_DAYS by default
   wis2node data clean


   # delete data older than --days (force override)
   wis2node data clean --days=$WIS2NODE_DATA_RETENTION_DAYS


Archiving
---------

Cleaning is performed on incoming data by default daily at 1Z by the system, and can also be run interactively with:

.. code-block:: bash

   wis2node data archive

Data is archived to ``WIS2NODE_DATADIR/data/archive``.
