.. _discovery-metadata:


Discovery metadata
==================

Discovery metadata describes a given dataset or collection. Data being published through a wis2box
requires discovery metadata (describing it) to be created, maintained and published to the wis2box
catalogue API.

wis2box supports managing discovery metadata using the WMO Core Metadata Profile (WCMP2) standard.

.. note::

   WCMP2 is currently in development as part of WMO activities.


Creating a discovery metadata record in wis2box is as easy as completing a YAML configuration file. wis2box
leverages the `pygeometa`_ project's `metadata control file (MCF)`_ format. Below is an example MCF file.


.. literalinclude:: ../../../../tests/data/metadata/discovery/mw-surface-weather-observations.yml
   :language: yaml

.. note::

   There are no conventions to the MCF filename. The filename does not get used/exposed or published.
   It is up to the user to determine the best filename, keeping in mind your wis2box system may manage
   and publish numerous datasets (and MCF files) over time.

.. _`pygeometa`: https://geopython.github.io/pygeometa
.. _`metadata control file (MCF)`: https://geopython.github.io/pygeometa/reference/mcf

.. _data-mappings:

Data mappings
-------------

A discovery metadata configuration file (MCF) has a `wis2box` section which provides a default data mapping (in YAML format).

The data mappings are indicated by the ``wis2box.data_mappings`` keyword, with each topic having a separate entry specifying:

- ``plugins``: all plugin objects associated with the topic, by file type/extension

Each plugin is based on the file extension to be detected and processed, with the following configuration:

- ``plugin``: the codepath of the plugin
- ``notify``: whether the plugin should publish a data notification
- ``template``: additional argument allowing a mapping template name to be passed to the plugin.  Note that if the path is relative, the plugin must be able to locate the template accordingly
- ``file-pattern``: additional argument allowing a file pattern to be passed to the plugin
- ``buckets``: the name(s) of the storage bucket(s) that data should be saved to (See :ref:`configuration` for more information on buckets)

See :ref:`extending-wis2box` for more information on adding your own data processing
pipeline.


Summary
-------

At this point, you have created discovery metadata for your given dataset(s).
