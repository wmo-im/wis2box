.. _data-mappings:

Data mappings
=============

Once a topic hierarchy is defined, it needs to be included in the wis2box data mappings
configuration. wis2box provides a default data mapping (in YAML format):

.. literalinclude:: ../../../../tests/data/data-mappings.yml
   :language: yaml

The data mappings are indicated by the ``data`` keyword, with each topic having a separate entry specifying:

- ``plugins``: all plugin objects associated with the topic, by file type/extension

Each plugin is based on the file extension to be detected and processed, with the following configuration:

- ``plugin``: the codepath of the plugin
- ``notify``: whether the plugin should publish a data notification
- ``template``: additional argument allowing a mapping template name to be passed to the plugin
- ``file-pattern``: additional argument allowing a file pattern to be passed to the plugin
- ``buckets``: the name(s) of the storage bucket(s) that data should be saved to (See :ref:`configuration` for more information on buckets)

The default data mapping can be overriden by user-defined data mappings with the following steps:

- create a YAML file similar to the above to include your topic hierarchy
- place the file in the ``WIS2BOX_DATADIR`` directory
- restart wis2box

See :ref:`extending-wis2box` for more information on adding your own data processing
pipeline.
