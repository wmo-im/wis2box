.. _data-mappings:

Data mappings
=============

Once a topic hierachy is define, it needs to be defined in the wis2box data mappings
configuration.  wis2box provides a default data mapping:

.. literalinclude:: ../../../wis2node/resources/data-mappings.yml
   :language: yaml

The format of the ``data`` property is ``key: value``, where:

- ``key``: the topic hierarchy defined in the system
- ``value``: the codepath that implements the relevant data processing

The default data mapping can be overriden by user-defined data mappings with the following steps:

- create a YAML file similar to the above to include your topic hierarchy
- set the ``WIS2NODE_DATA_MAPPINGS`` environment variable to point to the new file of definitions
- restart wis2node

See :ref:`extending-wis2node` for more information on adding your own data processing
pipeline.
