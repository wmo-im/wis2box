.. _data-retention:


Data retention
==============

wis2box is configured to set data retention according to your requirements. Data retention is managed
via the ``WIS2BOX_DATA_RETENTION_DAYS`` environment variable as part of configuring wis2box. Data
retention includes cleaning of published data and archiving of incoming/raw data.

Cleaning
--------

Cleaning is performed by default daily at 0Z by the system, and can also be run interactively with:


.. code-block:: bash

   # delete data older than WIS2BOX_DATA_RETENTION_DAYS by default
   wis2box data clean


   # delete data older than --days (force override)
   wis2box data clean --days=$WIS2BOX_DATA_RETENTION_DAYS


Archiving
---------

Cleaning is performed on incoming data by default daily at 1Z by the system, and can also be run interactively with:

.. code-block:: bash

   wis2box data archive

Data is archived to ``WIS2BOX_DATADIR/data/archive``.
