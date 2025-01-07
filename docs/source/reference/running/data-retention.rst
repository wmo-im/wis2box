.. _data-retention:


Data retention
==============

wis2box is configured to set data retention according to your requirements. Data retention is managed
via the ``WIS2BOX_STORAGE_DATA_RETENTION_DAYS`` and ``WIS2BOX_STORAGE_API_RETENTION_DAYS`` environment variables as part of configuring wis2box. 

Once a day, at UTC midnight, wis2box will run the commands ``wis2box data clean`` and ``wis2box api clean`` to remove data older than the specified retention period 
(cronjob defined in ``wis2box-management/docker/wis2box.cron``). 

Cleaning (storage)
-----------------

Cleaning applies to storage defined by ``WIS2BOX_STORAGE_PUBLIC`` and ``WIS2BOX_STORAGE_INCOMING`` and involves the deletion of files after set amount of time.

Cleaning is performed by default daily at 0Z by the system, and can also be run interactively with:

.. code-block:: bash

   # delete data older than WIS2BOX_STORAGE_DATA_RETENTION_DAYS by default
   wis2box data clean


   # delete data older than --days (force override)
   wis2box data clean --days=30


Cleaning (api)
--------------

Cleaning applies to data in the API backend and involves the deletion of records after a set amount of time.

Cleaning is performed by default daily at 0Z by the system, and can also be run interactively with:

.. code-block:: bash

   # delete data older than WIS2BOX_STORAGE_API_RETENTION_DAYS by default
   wis2box api clean

   # delete data older than --days (force override)
   wis2box api clean --days=30