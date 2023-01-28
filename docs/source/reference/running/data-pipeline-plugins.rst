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
to filter on incoming data based on a regular expression.  Consult the csv2bufr documentation
for more information on configuration and templating.

``wis2box.data.bufr4.ObservationDataBUFR2GeoJSON``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin converts BUFR observation data into GeoJSON using ``bufr2geojson``.  A ``file-pattern``
can be used to filter on incoming data based on a regular expression.  Consult the bufr2geojson documentation
for more information on configuration and templating.

``wis2box.data.geojson.ObservationDataGeoJSON``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin is for the purposes of publishing GeoJSON data to the API.

``wis2box.data.synop2bufr.SYNOP2BUFR``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin converts SYNOP ASCII data into BUFR using ``synop2bufr``.  A ``file-pattern`` can be used
to filter on incoming data based on a regular expression.  Note that the regex must contain two groups
(for year and month), which are used as part of synop2bufr processing.  Consult the synop2bufr documentation
for more information.

``wis2box.data.bufr4.ObservationDataBUFR``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin takes an incoming BUFR4 data file and separates it into individual BUFR bulletins if there
is more than one in a file.  Those bulletins are then further divided into individual subsets for publication
on WIS2.  As part of the process, files are quality checked for whitelisted WIGOS Station Identifiers and
valid location information.  Where these are missing, the information is either infilled using the wis2box
station list or the subset discarded if no match is found.  For processing efficiency, and to allow for
concurrent processing, it is recommended that the input data to this plugin is already separated into one
BUFR message per file and one subset per message.

.. _`csv2bufr`: https://csv2bufr.readthedocs.io
.. _`bufr2geojson`: https://github.com/wmo-im/bufr2geojson
.. _`synop2bufr`: https://github.com/wmo-im/synop2bufr
