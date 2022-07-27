.. _minio:

Overview
========

The default storage for wis2box is MinIO, an S3 compatible object storage layer.

The MinIO UI can be accessed locally on the host at http://localhost:9001

The username/password for MinIO is configured through environment variables, see the :ref:`configuration` section. 
The default is minio/minio123

.. image:: /_static/minio_login_screen.png
   :width: 800px
   :alt: minio_login_screen.png 
   :align: center

The content of the buckets can be browser through the MinIO UI by selecting a bucket:

.. image:: /_static/minio_buckets.png
   :width: 800px
   :alt: minio_buckets.png 
   :align: center

Files can uploaded to the MinIO bucket in various ways. Any new file received on MinIO will trigger a notification received by wis2box.

Below we have documented a few basic examples on how to send data to the MinIO 'wis2box-incoming'-bucket.
Please check https://docs.min.io for further documentation on how to use MinIO and other MinIO SDKs

upload using the Python Client API
----------------------------------

Install the minio module for python using pip:

.. code-block:: bash

    pip3 install minio

Python-example to copy a local file called 'myfile.csv' into the wis2box-incoming bucket, using topic-hierachy foo.bar.baz:

.. code-block:: python

    from minio import Minio

    client = Minio(
        "localhost",
        access_key="minio",
        secret_key="minio123",
        secure=False
    )

    client.fput_object(
        "wis2box-incoming", "myfile.csv", "/foo/bar/baz/myfile.csv",
    ) 

upload using S3cmd
------------------

Install S3cmd from http://s3tools.org/s3cmd , on the host running wis2box-stack

Edit the following fields in your s3cmd configuration file ~/.s3cfg

.. code-block:: bash

    # Setup endpoint
    host_base = localhost:9000
    use_https = False

    # Setup access keys
    access_key = minio
    secret_key = minio123

cmd-line example to copy a local file called 'myfile.csv' into the wis2box-incoming bucket, using topic-hierachy foo.bar.baz:

.. code-block:: bash

    s3cmd myfile.csv s3://wis2box-incoming/foo/bar/baz

upload using the MinIO UI
-------------------------

Files can also be uploaded into the wis2box-incoming bucket from the MinIO UI:

.. image:: /_static/minio_upload_files.png
   :width: 800px
   :alt: minio_upload_files.png 
   :align: center