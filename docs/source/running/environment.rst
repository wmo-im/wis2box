.. _environment:

Environment
===========

wis2box requires the environment to be initialized before data processing or publishing.

.. code-block:: bash

   wis2box environment create

This command will create all the directories required. You can check the environment at
any time with:

.. code-block:: bash

   wis2box environment show

For the purposes of documentation, the value ``WIS2BOX_DATADIR`` represents the base
directory for all data managed in wis2box.
