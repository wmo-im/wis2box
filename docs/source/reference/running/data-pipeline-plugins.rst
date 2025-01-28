.. _data-pipeline-plugins:

Data pipeline plugins
=====================

Driven by topic hierarchies, wis2box is a plugin architecture orchestrating all the
required components of a WIS2 Node.  wis2box also provides a data pipeline plugin
architecture which allows for users to define a plugin based on a topic hierarchy to
publish incoming data (see :ref:`data-mappings` for more information).


.. seealso:: :ref:`extending-wis2box`
.. seealso:: :ref:`data-mappings`

Default pipeline plugins
------------------------

wis2box provides a number of data pipeline plugins by default, which users can be used "out of the box".  The
list below describes each plugin and provides an example data mappings configuration.

.. _csv2bufr-plugin:

``wis2box.data.csv2bufr.ObservationDataCSV2BUFR``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin converts CSV observation data into BUFR using `csv2bufr`_. 

A `template` is required to convert the CSV columns to BUFR encoded values, you can use the built-in templates or create your own custom template.

A ``file-pattern`` is used to filter on incoming data based on a regular expression.  

A typical csv2bufr plugin workflow using one of the built-in templates would be defined as follows:

.. code-block:: yaml

   csv:
       - plugin: wis2box.data.csv2bufr.ObservationDataCSV2BUFR
         template: aws-template # using one of the built-in templates
         notify: true  # trigger GeoJSON publishing for API and UI
         file-pattern: '^.*\.csv$'

In this the example `aws-template` refers to the `aws_example.json` template defined by the `csv2bufr-templates`_ repository.

Environment variables can be set in `wis2box.env` to customize the behavior of the csv2bufr-plugin within the wis2box, see `csv2bufr-environment-variables`_ for the full list of environment variables.

Using the csv2bufr plugin with a custom template
++++++++++++++++++++++++++++++++++++++++++++++++

For example, to create a custom template for the csv2bufr plugin, follow these steps:

Login to the wis2box-api container:

.. code-block:: bash

    python3 wis2box-ctl.py login wis2box-api

Within the wis2box-api container you can using the command `csv2bufr mappings create` and provide the BUFR-descriptors you want to encode as arguments.
Make sure to redirect the output to a file in the `/data/wis2box/mappings` directory (which is mapped to the host system at `$WIS2BOX_HOST_DATADIR/mappings`)

For example, to create a custom template for the csv2bufr plugin with the BUFR-descriptors 301150, 301011, 301012, 301021, 007031, 302001, run the following command:

.. code-block:: bash

     csv2bufr mappings create 301150 301011 301012 301021 007031 302001 --output /data/wis2box/mappings/my_own_template.json

See the `Manual on Codes`_ to find the BUFR-descriptors you need.

Exit the container after creating the custom template:

.. code-block:: bash

    exit

You can edit the template file on the host system at `$WIS2BOX_HOST_DATADIR/mappings/my_own_template.json` to customize the template further.

After creating the custom template, you can use it in the csv2bufr plugin configuration in MCF as follows:

.. code-block:: yaml

   csv:
       - plugin: wis2box.data.csv2bufr.ObservationDataCSV2BUFR
         template: /data/wis2box/mappings/my_own_template.json  # locally created csv2bufr mapping (located in $WIS2BOX_HOST_DATADIR/mappings)
         notify: true  # trigger GeoJSON publishing for API and UI
         file-pattern: '^.*\.csv$'

And/or you can select the new template in the Plugin Configuration of the Dataset Mappings Editor in the wis2box-webapp:

.. image:: ../_static/csv2bufr_custom_template.png
   :alt: csv2bufr custom template
   :align: center

``wis2box.data.bufr4.ObservationDataBUFR2GeoJSON``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin is typically used for wis2box API publication, and converts BUFR
observation data into GeoJSON using ``bufr2geojson``.  A ``file-pattern``
can be used to filter on incoming data based on a regular expression.  Consult the `bufr2geojson`_ documentation
for more information on configuration and templating.

A typical bufr2geojson plugin workflow definition would be defined as follows:

.. code-block:: yaml

   bufr4:
       - plugin: wis2box.data.bufr2geojson.ObservationDataBUFR2GeoJSON
         file-pattern: '^.*\.bufr4$'


``wis2box.data.geojson.ObservationDataGeoJSON``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin is for the purposes of publishing GeoJSON data to the API.

``wis2box.data.synop2bufr.SYNOP2BUFR``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin converts SYNOP ASCII data into BUFR using ``synop2bufr``.  A ``file-pattern`` can be used
to filter on incoming data based on a regular expression.

Note that the regular expression **must** contain two groups (for 4-digit year and 2-digit month), which are used as part of synop2bufr processing.  Consult the `synop2bufr`_ documentation for more information.

A typical synop2bufr plugin workflow definition would be defined as follows:

.. code-block:: yaml

   txt:
       - plugin: wis2box.data.synop2bufr.ObservationDataSYNOP2BUFR
         notify: true  # trigger GeoJSON publishing for API and UI
         file-pattern: '^station_123_(\d{4})(\d{2}).*.txt$'  # example: station_123_202305_112342.txt (where 2023 is the year and 05 is the month)

``wis2box.data.bufr4.ObservationDataBUFR``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin takes an incoming BUFR4 data file and separates it into individual BUFR bulletins if there
is more than one in a file.  Those bulletins are then further divided into individual subsets for publication
on WIS2.  As part of the process, files are quality checked for valid WIGOS Station Identifiers and
location information.  Where these are missing, the information is either infilled using the wis2box
station list or the subset discarded if no match is found.  Missing temporal information results in the data
being discarded.

For processing efficiency, and to allow for concurrent processing, it is recommended that the input data
to this plugin is already separated into one BUFR message per file and one subset per message.

A typical BUFR4 plugin workflow definition would be defined as follows:

.. code-block:: yaml

   bin:
       - plugin: wis2box.data.bufr4.ObservationDataBUFR
         notify: true  # trigger GeoJSON publishing for API and UI
         file-pattern: '^.*\.bin$'

.. _cap-message-data-plugin:

``wis2box.data.cap_message.CAPMessageData``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin takes the incoming XML file, then validates it against the
`CAP v1.2 schema <https://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html>`_
and optionally verifies the digital signature before publishing.

The validation is performed using the `capvalidator <https://github.com/wmo-im/capvalidator>`_
package.

A typical CAP message plugin workflow definition would be defined as follows:

.. code-block:: yaml

   xml:
       - plugin: wis2box.data.cap_message.CAPMessageData
         notify: true
          buckets:
            - ${WIS2BOX_STORAGE_INCOMING}
         file-pattern: '^.*\.xml$'

By default the XML signature validation is set to ``False``. To enable the validation add the following environment variable to your ``wis2box.env`` file:

.. code-block:: bash

    CHECK_CAP_SIGNATURE=True

``wis2box.data.universal.UniversalData``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin can be used to publish any data, without any transformation.

The plugin takes any incoming data, copies it to the ``/data`` endpoint configured in wis2box, providing minimal information in the WIS2 Notification:

- ``properties.datatime`` in the WIS2 notification is parsed as ``match.group(1)`` of the regular expression defined in the plugin configuration. If the group cannot be parsed by ``dateutil.parser``, an error will be raised and the data will not be published
- ``geometry`` in the WIS2 Notification will be null

For example, to publish GRIB2 data matching the file-pattern ``^.*_(\d{8})\d{2}.*\.grib2$`` the following configuration could be used:

.. code-block:: yaml

    grib2:
        - plugin: wis2box.data.universal.UniversalData
          notify: true
          buckets:
            - ${WIS2BOX_STORAGE_INCOMING}
          file-pattern: '^.*_(\d{8})\d{2}.*\.grib2$' # example: Z_NAFP_C_BABJ_20231207000000_P_CMA-GEPS-GLB-036.grib2 (where 20231207000000 will be used as the datetime)


See :ref:`data-mappings` for a full example data mapping configuration.

.. _`csv2bufr`: https://csv2bufr.readthedocs.io/en/v0.8.5/
.. _`csv2bufr-environment-variables`: https://csv2bufr.readthedocs.io/en/v0.8.5/installation.html#environment-variables
.. _`csv2bufr-templates`: https://github.com/wmo-im/csv2bufr-templates
.. _`bufr2geojson`: https://github.com/wmo-im/bufr2geojson
.. _`synop2bufr`: https://synop2bufr.readthedocs.io

.. _`Manual on Codes`: https://library.wmo.int/records/item/35625-manual-on-codes-volume-i-2-international-codes