.. _troubleshooting:

Troubleshooting
===============

This page lists several commonly seen issues and how to address them.

'./docker-compose.yml' is invalid
---------------------------------

When starting wis2box you see the errors:

.. code-block:: bash
    
    ERROR: The Compose file './docker-compose.yml' is invalid because:
    Unsupported config option for volumes: 'auth-data'
    Unsupported config option for services: 'wis2box-auth'

check the version of docker compose you are running with:

.. code-block:: bash
    
    docker compose --version

if not 1.29.2 you can install this using the following docker compose:

.. code-block:: bash

    # download docker compose 1.29.2
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    # set executable
    sudo chmod +x /usr/local/bin/docker-compose
    # remove current version
    sudo rm /usr/bin/docker-compose
    # set link to downloaded version
    sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

	
OSError: Missing data mappings
------------------------------

The wis2box logging displays the error:

.. code-block:: bash	
    
    OSError: Missing data mappings: [Errno 2] No such file or directory: '/data/wis2box/data-mappings.yml'

Check your dev.env and check value that was set for WIS2BOX_HOST_DATADIR

.. code-block:: bash
    
    WIS2BOX_HOST_DATADIR=/home/wmouser/wis2box-data

In this case the value set was '/home/wmouser/wis2box-data'

Check that the file 'data-mappings.yml' is contained in this directory:

.. code-block:: bash
    
    ls -lh /home/wmouser/wis2box-data/data-mappings.yml

After you have ensured the data-mappings.yml is in the directory defined by WIS2BOX_HOST_DATADIR, restart the wis2box:

.. code-block:: bash
    
    python3 wis2box-ctl.py stop
    python3 wis2box-ctl.py start

Topic Hierarchy validation error: Unknown file type
---------------------------------------------------

Check your ``data-mappings.yml`` file to adjust the file extension expected by the plugins processing your dataset. 

If you are ingesting files with extension .bin:

.. code-block:: bash

        plugins:
            bin:
                - plugin: wis2box.data.bufr4.ObservationDataBUFR
                  notify: true
                  buckets:
                    - ${WIS2BOX_STORAGE_INCOMING}
                  file-pattern: '*'


If you are ingesting files with extension ``.b``:

.. code-block:: bash

        plugins:
            b:
                - plugin: wis2box.data.bufr4.ObservationDataBUFR
                  notify: true
                  buckets:
                    - ${WIS2BOX_STORAGE_INCOMING}
                  file-pattern: '*'

The Access Key Id you provided does not exist in our records
------------------------------------------------------------

If you see this error when uploading data to the wis2box-incoming storage, you have provided the wrong username and/or password to access MinIO.
Check the values for ``WIS2BOX_BROKER_USERNAME`` and ``WIS2BOX_BROKER_PASSWORD`` you have provided in your ``dev.env`` file. 
The default username/password for MinIO is ``minio/minio123``.

Topic Hierarchy validation error: No plugins for ... in data mappings
---------------------------------------------------------------------

A file arrived a folder for which no matching dataset was defined in your ``data-mappings.yml``.

For dataset ``foo.bar``, store your file in the path ``/foo/bar/``.

This requires either updating ``data-mappings.yml`` or changing the target folder under which the file is received.

ERROR - Failed to publish, wsi: ..., tsi: XXXXX
-----------------------------------------------

Data arrived for a station that is not present in the station metadata cache. 
To add missing stations, update the file ``metadata/station/station_list.csv`` in the wis2box data directory (see :ref:`setup`).

Error: no such container: wis2box-management
--------------------------------------------

If the wis2box-management container is not running the 'login' command will fail. 
The wis2box-management container depends on other services being available before it can successfully started.

Please check all services are Running using the following command:

.. code-block:: bash

    python3 wis2box-ctl.py status

Possible issues are:

- port 80 is already in use, the nginx-service will fail to start if there is already a web-server running on your instance
- WIS2BOX_STORAGE_PASSWORD is too short, minio will fail to start if you specify a WIS2BOX_STORAGE_PASSWORD of less than 8 characters

wisbox-UI is empty
------------------

If when you access the wis2box-UI you see the interface but no datasets are visible, check the WIS2BOX_URL and WIS2BOX_API_URL are set correctly.

Please note that after changing the WIS2BOX_URL and WIS2BOX_API_URL, you will have to restart your wis2box:

.. code-block:: bash

  python3 wis2box-ctl.py stop
  python3 wis2box-ctl.py start

And repeat the commands for adding your dataset and publishing your metadata, to ensure the URLs are updated in the records:

.. code-block:: bash

  python3 wis2box-ctl.py login
  wis2box data add-collection ${WIS2BOX_HOST_DATADIR}/surface-weather-observations.yml
  wis2box metadata discovery publish ${WIS2BOX_HOST_DATADIR}/surface-weather-observations.yml
