.. _data-pipeline-plugins:

Data pipeline plugins
=====================

Driven by topic hierarchies, wis2box is a plugin architecture orchestrating all the
required components of a WIS2 node.  wis2box also provides a data pipeline plugin
architecture which allows for users to define a plugin based on a topic hierarchy to
publish incoming data (see :ref:`data-mappings` for more information).


.. seealso:: :ref:`extending-wis2box`
.. seealso:: :ref:`data-mappings`

Default pipeline plugins
------------------------

wis2box provides a number of data pipeline plugins which users can be used "out of the box".

``wis2box.data.csv2bufr.ObservationDataCSV2BUFR``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin converts CSV observation data into BUFR using ``csv2bufr``.  A csv2bufr template
can be configured to process the data accordingly.  In addition, ``file-pattern`` can be used
to filter on incoming data based on a regular expression.  Consult the `csv2bufr`_ documentation
for more information on configuration and templating.

A typical csv2bufr plugin workflow would like:

.. code-block:: yaml

   csv:
       - plugin: wis2box.data.csv2bufr.ObservationDataCSV2BUFR
         template: /data/wis2box/synop_bufr.json  # locally created csv2bufr mapping (located in $WIS2BOX_HOST_DATADIR)
         notify: true  # trigger GeoJSON publishing for API and UI
         file-pattern: '^.*\.csv$'


``wis2box.data.bufr4.ObservationDataBUFR2GeoJSON``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin is typically used for wis2box API publication, and converts BUFR
observation data into GeoJSON using ``bufr2geojson``.  A ``file-pattern``
can be used to filter on incoming data based on a regular expression.  Consult the `bufr2geojson`_ documentation
for more information on configuration and templating.

A typical bufr2geojson plugin workflow would like:

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
to filter on incoming data based on a regular expression.  Note that the regex **must** contain two groups
(for 4-digit year and 2-digit month), which are used as part of synop2bufr processing.  Consult the `synop2bufr`_ documentation
for more information.

A typical synop2bufr plugin workflow would like:

.. code-block:: yaml

   txt:
       - plugin: wis2box.data.synop2bufr.ObservationDataSYNOP2BUFR
         notify: true  # trigger GeoJSON publishing for API and UI
         file-pattern: '^A_SMR.*EDZW_(\d{4})(\d{2}).*.txt$'


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

A typical BUFR4 plugin workflow would like:

.. code-block:: yaml

   bin:
       - plugin: wis2box.data.bufr4.ObservationDataBUFR
         notify: true  # trigger GeoJSON publishing for API and UI
         file-pattern: '^.*\.bin$'


See :ref:`data-mappings` for a full example data mapping configuration.

.. _`csv2bufr`: https://csv2bufr.readthedocs.io
.. _`bufr2geojson`: https://github.com/wmo-im/bufr2geojson
.. _`synop2bufr`: https://synop2bufr.readthedocs.io
