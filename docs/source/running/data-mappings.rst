.. _data-mappings:

Data mappings
=============

Once a topic hierarchy is defined, it needs to be included in the wis2box data mappings
configuration. wis2box provides a default data mapping (in yaml format):

.. literalinclude:: ../../../wis2box/resources/data-mappings.yml
   :language: yaml

The data mappings are indicated by the ``data`` keyword, with each topic having a separate entry specifying:

- ``plugin``: the codepath of the plugin.
- ``template``: additional argument allowing a mapping template name to be passed to the plugin.
- ``file-pattern``: additional argument allowing a file pattern to be passed to the plugin.

The default data mapping can be overriden by user-defined data mappings with the following steps:

- create a YAML file similar to the above to include your topic hierarchy
- set the ``WIS2BOX_DATADIR_DATA_MAPPINGS`` environment variable to point to the new file of definitions
- restart wis2box

See :ref:`extending-wis2box` for more information on adding your own data processing
pipeline.
