.. _troubleshooting:

Troubleshooting
===============

This section summarizes how to troubleshoot commonly seen issues when setting up a wis2box for data-sharing on the WIS 2.0 network.

To check for errors you can check the logs from the command-line:

.. code-block:: bash
    
    python3 wis2box-ctl.py logs

Or use the Grafana-UI, which is exposed at port 3000 on our local wis2box-host.

'./docker/docker-compose.yml' is invalid
----------------------------------------

When starting wis2box you see the errors:

.. code-block:: bash
    
    ERROR: The Compose file './docker/docker-compose.yml' is invalid because:
    Unsupported config option for volumes: 'auth-data'
    Unsupported config option for services: 'wis2box-auth'

check the version of docker-compose you are running with:

.. code-block:: bash
    
    docker-compose --version

if not 1.29.2 you can install this using the following docker-compose :

.. code-block:: bash

    # download docker-compose 1.29.2
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

Check your data-mappings.yml file to adjust the file extension expected by the plugins processing your dataset. 

If you are ingesting files with extension .bin:

.. code-block:: bash

        plugins:
            bin:
                - plugin: wis2box.data.bufr4.ObservationDataBUFR
                  notify: true
                  buckets:
                    - ${WIS2BOX_STORAGE_INCOMING}
                  file-pattern: '*'


If you are ingesting files with extension .b:

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
Check the values for WIS2BOX_BROKER_USERNAME and WIS2BOX_BROKER_PASSWORD you have provided in your dev.env file. 
The default username/password for MinIO is minio/minio123

Topic Hierarchy validation error: No plugins for ... in data mappings
---------------------------------------------------------------------

A file arrived a folder for which no matching dataset was defined in your data-mappings.yml. 

For dataset='foo.bar', store your file in the path '/foo/bar/'

You need to either update your data-mappings.yml or change the target-folder in which the file is received.

ERROR - Failed to publish, wsi: ..., tsi: XXXXX
-----------------------------------------------

Data arrived for a station that is not present in the stations-metadata cache. 
To add missing stations create a new 'station_list.csv' and update the stations-cache using the command 'wis2box metadata station sync' (see :ref:`wis2box-setup`)