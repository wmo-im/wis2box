.. _data-ingest:

Data ingest setup
=================

The runtime component of wis2box is data ingestion. This is an event driven workflow driven by S3 notifications from uploading data to wis2box storage.

The wis2box storage is provided using a `MinIO`_ container that provides S3-compatible object storage.

Any file received in the ``wis2box-incoming`` storage bucket will trigger an action to process the file. 
What action to take is determined by the ``data-mappings.yml`` you've setup in the previous section.

MinIO user interface
--------------------

To access the MinIO user interface, visit ``http://localhost:9001`` in your web browser.

You can login with your ``WIS2BOX_STORAGE_USERNAME`` and ``WIS2BOX_STORAGE_PASSWORD``:

.. image:: ../_static/minio-login-screen2.png
    :width: 400
    :alt: MinIO login screen

To test the data ingest, add a sample file for your observations in the ``wis2box-incoming`` storage bucket.

Select 'browse' on the ``wis2box-incoming`` bucket and select 'Choose or create a new path' to define a new folder path:

.. image:: ../_static/minio-new-folder-path.png
    :width: 800
    :alt: MinIO new folder path

.. note::
    The folder in which the file is placed defines the dataset for the data you are sharing.  For example, for dataset ``foo.bar``, store your file in the path ``/foo/bar/``. 
    
    The path is also used to define the topic hierarchy for your data (see `WIS2 topic hierarchy`_). The first 3 levels of the WIS2 topic hierarchy ``origin/a/wis2`` are automatically included by wis2box when publishing data notification messages.

    * The error message ``Topic Hierarchy validation error: No plugins for minio:9000/wis2box-incoming/... in data mappings`` indicates you stored a file in a folder for which no matching dataset was defined in your ``data-mappings.yml``.

After uploading a file to ``wis2box-incoming`` storage bucket, you can browse the content in the ``wis2box-public`` bucket.  If the data ingest was successful, new data will appear as follows:

.. image:: ../_static/minio-wis2box-public.png
    :width: 800
    :alt: MinIO wis2box-public storage bucket

If no data appears in the ``wis2box-public`` storage bucket, you can inspect the logs from the command line:

.. code-block:: bash

   python3 wis2box-ctl.py logs wis2box

Or by visiting the local Grafana instance running at ``http://localhost:3000``

wis2box workflow monitoring
---------------------------

The Grafana homepage shows an overview with the number of files received, new files produced and messages published.

Pay attention to the messages reported in the wis2box logs (right hand side) which indicates errors encountered during data processing:

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
    minio_path = '/ita/italy_wmo_demo/data/core/weather/surface-based-observations/synop/'

    endpoint = 'http://localhost:9000'
    WIS2BOX_STORAGE_USERNAME = 'wis2box-storage-user'
    WIS2BOX_STORAGE_PASSWORD = '<your-unique-password>'

    client = Minio(
        endpoint=endpoint,
        access_key=WIS2BOX_STORAGE_USERNAME,
        secret_key=WIS2BOX_STORAGE_PASSWORD,
        secure=is_secure=False)
    
    filename = filepath.split('/')[-1]
    client.fput_object('wis2box-incoming', minio_path+filename, filepath)

wis2box-ftp
-----------

You can add an additional service to allow your data to be accessible over FTP with the following command

.. code-block:: bash

    docker-compose -f docker-compose.wis2box-ftp.yml -p wis2box_project --env-file dev.env

You will need to define the following additional environment-variables to your dev.env to define the FTP username and password:

.. code-block:: bash

    FTP_USER=<your-ftp-username>
    FTP_PASSWORD=<your-ftp-password>

See the GitHub repository `wis2box-ftp`_ for more information on this service.

Next steps
----------

After you have successfully setup your data ingest process into the wis2box, you are ready to share your data with the global
WIS2 network by enabling external access to your public services.

Next: :ref:`public-services-setup`

.. _`MinIO`: https://min.io/docs/minio/container/index.html
.. _`wis2box-ftp`: https://github.com/wmo-im/wis2box-ftp
.. _`WIS2 topic hierarchy`: https://github.com/wmo-im/wis2-topic-hierarchy
