.. _data-retention:


Data retention
==============

wis2box is configured to set data retention according to your requirements. Data retention is managed
via the ``WIS2BOX_STORAGE_DATA_RETENTION_DAYS`` environment variable as part of configuring wis2box. 

Cleaning
--------

Cleaning applies to storage defined by ``WIS2BOX_STORAGE_PUBLIC`` and involves the deletion of files after set amount of time.

Cleaning is performed by default daily at 0Z by the system, and can also be run interactively with:

.. code-block:: bash

   # delete data older than WIS2BOX_STORAGE_DATA_RETENTION_DAYS by default
   wis2box data clean


   # delete data older than --days (force override)
   wis2box data clean --days=30


Archiving
---------

Archiving applies to storage defined by ``WIS2BOX_STORAGE_INCOMING`` and involves moving files to the storage defined by ``WIS2BOX_STORAGE_ARCHIVE``. 

Archive is performed on incoming data by default daily at 1Z by the system, and can also be run interactively with:

.. code-block:: bash

   wis2box data archive

Only files with a timestamp older than one hour are considered for archiving.
