.. _api-publishing:

API publishing
==============

At this stage:

- station metadata has been configured
- discovery metadata has been created
- data pipelines are configured and running

Let's dive into publishing the data and metadata:

wis2box provides an API supporting the `OGC API`_ standards using `pygeoapi`_.

Station metadata API publishing
-------------------------------

The first step is to publish our station metadata to the API. The command below
will generate local station collection GeoJSON for pygeoapi publication.

.. code-block:: bash

   wis2box metadata station publish-collection


Discovery metadata API publishing
---------------------------------

This step will publish dataset discovery metadata to the API.

.. code-block:: bash

   wis2box metadata discovery publish /path/to/discovery-metadata.yml


Dataset collection API publishing
---------------------------------

The below command will add the dataset collection to pygeoapi from the
discovery metadata MCF created as described in the :ref:`discovery-metadata` section.

.. code-block:: bash

   wis2box api add-collection $WIS2BOX_DATADIR/data/config/foo/bar/baz/discovery-metadata.yml --topic-hierarchy foo.bar.baz

To delete the colection from the API backend and configuration:

.. code-block:: bash

   wis2box api delete-collection --topic-hierarchy foo.bar.baz


Note that the data itself is being published to the API backend automatically given the event
driven workflow. If manual ingest is needed, the following command can be run in interactive mode:

.. code-block:: bash

   wis2box api add-collection-items --topic-hierarchy foo.bar.baz

API container restart
---------------------

Any change to API configuration requires a restart of the API container, which can be run via the following:

.. code-block:: bash

   python3 wis2box-ctl.py restart wis2box

Summary
-------

At this point, you have successfully published the required data and metadata collections to the API.


.. _`OGC API`: https://ogcapi.ogc.org
.. _`pygeoapi`: https://pygeoapi.io
