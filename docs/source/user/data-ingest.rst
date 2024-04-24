.. _data-ingest:

Data ingest setup
=================

The runtime component of wis2box is data ingestion. This is an event driven workflow driven by S3 notifications from uploading data to wis2box storage.

The wis2box storage is provided using a `MinIO`_ container that provides S3-compatible object storage.

Any file received in the ``wis2box-incoming`` storage bucket will trigger an action to process the file. 
What action to take is determined by the data mappings that were setup in the previous section.

wis2box-webapp
--------------

The wis2box-webapp is a web application that includes the following forms for data validation and ingestion:

* user interface to ingest SYNOP data
* user interface to ingest CSV data 

The wis2box-webapp is available on your host at `http://<your-public-ip>/wis2box-webapp`.

Interactive data ingestion requires an execution token, which can be generated using the ``wis2box auth add-token`` command inside the wis2box-management container:

.. code-block:: bash

    python3 wis2box-ctl.py login
    wis2box auth add-token --path processes/wis2box

.. note::

   Be sure to record the token value, as it will not be shown again. If you lose the token, you can generate a new one.

data mappings plugins
---------------------

The plugins you have configured for your dataset mappings will determine the actions taken when data is received in the MinIO storage bucket.

The wis2box provides 3 types of built-in plugins to publish data in BUFR format:

* `bufr2bufr` : the input is received in bufr format and split by subset, where each subset is published as a separate bufr message
* `synop2bufr` : the input is received in FM-12 synop format and converted to bufr format. The year and month are extracted from the file-pattern
* `csv2bufr` : the input is received in csv format and converted to bufr format

When using the csv2bufr plugin, the columns are mapped to bufr-encoded values using a mappings-template.
You can find the reference for the built-in 'AWS'-mappings template here [aws-full.csv](../_static/aws-full.csv)

To publish data for other data-formats you can use the 'Universal' plugin, which will pass through the data without any conversion.
Please note that you will need to ensure that the date-timestamp can be extracted from the file-pattern when using this plugin.

MinIO user interface
--------------------

To access the MinIO user interface, visit ``http://<your-host-ip>:9001`` in your web browser.

You can login with your ``WIS2BOX_STORAGE_USERNAME`` and ``WIS2BOX_STORAGE_PASSWORD``:

.. image:: ../_static/minio-login-screen2.png
    :width: 400
    :alt: MinIO login screen

.. note::

   The ``WIS2BOX_STORAGE_USERNAME`` and ``WIS2BOX_STORAGE_PASSWORD`` are defined in the ``wis2box.env`` file.

To test the data ingest, add a sample file for your observations in the ``wis2box-incoming`` storage bucket.

Select 'browse' on the ``wis2box-incoming`` bucket and select 'Choose or create a new path' to define a new folder path:

.. image:: ../_static/minio-new-folder-path.png
    :width: 800
    :alt: MinIO new folder path

.. note::
    The folder in which the file is placed defines the topic you want to share the data on and should match the datasets defined in your data mappings.
    
    The first 3 levels of the WIS2 topic hierarchy ``origin/a/wis2`` are automatically included by wis2box when publishing data notification messages.

    For example:
    
    * data to be published on: ``origin/a/wis2/cd-brazza_met_centre/data/core/weather/surface-based-observations/synop``
    * upload data in the path: ``cd-brazza_met_centre/data/core/weather/surface-based-observations/synop``
    
    The error message ``Topic Hierarchy validation error: No plugins for minio:9000/wis2box-incoming/... in data mappings`` indicates you stored a file in a folder for which no matching dataset was defined in the data mappings.

After uploading a file to ``wis2box-incoming`` storage bucket, you can browse the content in the ``wis2box-public`` bucket.  If the data ingest was successful, new data will appear as follows:

.. image:: ../_static/minio-wis2box-public.png
    :width: 800
    :alt: MinIO wis2box-public storage bucket

If no data appears in the ``wis2box-public`` storage bucket, you can inspect the logs from the command line:

.. code-block:: bash

   python3 wis2box-ctl.py logs wis2box

Or by visiting the local Grafana instance running at ``http://<your-host-ip>:3000``

wis2box workflow monitoring
---------------------------

The Grafana homepage shows an overview with the number of files received, new files produced and WIS2 notifications published.

The `Station data publishing status` panel (on the left side) shows an overview of notifications and failures per configured station.

The `wis2box ERRORs` panel (on the bottom) prints all ERROR messages reported by the wis2box-management container.

.. image:: ../_static/grafana-homepage.png
    :width: 800
    :alt: wis2box workflow monitoring in Grafana

Once you have verified that the data ingest is working correctly you can prepare an automated workflow to send your data into wis2box.

Automating data ingestion
-------------------------

See below a Python example to upload data using the MinIO package:

.. code-block:: python

    import glob
    import sys

    from minio import Minio

    filepath = '/home/wis2box-user/local-data/mydata.bin'
    minio_path = '/it-roma_met_centre/data/core/weather/surface-based-observations/synop/'

    endpoint = 'http://localhost:9000'
    WIS2BOX_STORAGE_USERNAME = 'wis2box'
    WIS2BOX_STORAGE_PASSWORD = '<your-wis2box-storage-password>'

    client = Minio(
        endpoint=endpoint,
        access_key=WIS2BOX_STORAGE_USERNAME,
        secret_key=WIS2BOX_STORAGE_PASSWORD,
        secure=is_secure=False)
    
    filename = filepath.split('/')[-1]
    client.fput_object('wis2box-incoming', minio_path+filename, filepath)

.. note::
    
    In the example the file ``mydata.bin`` in ingested from the directory ``/home/wis2box-user/local-data/`` on the host running wis2box.
    If you are running the script on the same host as wis2box, you can use the endpoint ``http://localhost:9000`` as in the example. 
    Otherwise, replace localhost with the IP address of the host running wis2box. 

wis2box-ftp
-----------

You can add an additional service to allow your data to be accessible over FTP.

To use the ``docker-compose.wis2box-ftp.yml`` template included in wis2box, create a new file called ``ftp.env`` using any text editor, and add the following content:

.. code-block:: bash

    MYHOSTNAME=hostname.domain.tld

    FTP_USER=wis2box
    FTP_PASS=wis2box123
    FTP_HOST=${MYHOSTNAME}

    WIS2BOX_STORAGE_ENDPOINT=http://${MYHOSTNAME}:9000
    WIS2BOX_STORAGE_USERNAME=wis2box
    WIS2BOX_STORAGE_PASSWORD=XXXXXXXX

    LOGGING_LEVEL=INFO

ensure ``MYHOSTNAME`` is set to **your** hostname (fully qualified domain name) and ``WIS2BOX_STORAGE_PASSWORD`` is set to **your** MinIO password.

Then start the ``wis2box-ftp`` service with the following command:

.. code-block:: bash

    docker compose -f docker-compose.wis2box-ftp.yml --env-file ftp.env up -d

When using the wis2box-ftp service to ingest data, please note that the topic is determined by the directory structure in which the data arrives.

For example, to correctly ingest data on the topic ``it-roma_met_centre.data.core.weather.surface-based-observations.synop`` you need to copy the data into the directory ``/it-roma_met_centre/data/core/weather/surface-based-observations/synop`` on the FTP server:

.. image:: ../_static/winscp_wis2box-ftp_example.png
    :width: 600
    :alt: Screenshot of WinSCP showing directory structure in wis2box-ftp

See the GitHub repository `wis2box-ftp`_ for more information on this service.

wis2box-data-subscriber
-----------------------

.. note::

   This service currently only works with Campbell scientific data loggers version CR1000X.

You can add an additional service on the host running your wis2box instance to allow data to be received over MQTT.

This service subscribes to the topic ``data-incoming/#`` on the wis2box broker and parses the content of received messages and publishes the result in the ``wis2box-incoming`` bucket.

To start the ``wis2box-data-subscriber``, add the following additional variables to ``wis2box.env``:

.. code-block:: bash

    CENTRE_ID=zm-zmb_met_centre  # set centre_id for wis2-topic-hierarchy

These variables determine the destination path in the ``wis2box-incoming`` bucket:

``{CENTRE_ID}/data/core/weather/surface-based-observations/synop/``

You then you can activate the optional 'wis2box-data-subscriber' service as follows:

.. code-block:: bash

    docker compose -f docker-compose.data-subscriber.yml --env-file wis2box.env up -d

See the GitHub `wis2box-data-subscriber`_ repository for more information on this service.

Next steps
----------

After you have successfully setup your data ingest process into the wis2box, you are ready to share your data with the global
WIS2 network by enabling external access to your public services.

Next: :ref:`public-services-setup`

.. _`MinIO`: https://min.io/docs/minio/container/index.html
.. _`wis2box-ftp`: https://github.com/wmo-im/wis2box-ftp
.. _`wis2box-data-subscriber`: https://github.com/wmo-im/wis2box-data-subscriber
.. _`WIS2 topic hierarchy`: https://github.com/wmo-im/wis2-topic-hierarchy
