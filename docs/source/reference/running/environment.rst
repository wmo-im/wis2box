.. _environment:

Environment
===========

wis2box initializes the environment when starting, before data processing or publishing. To
view the environment, run the following command:

.. code-block:: bash

   wis2box environment show

For the purposes of documentation, the value ``WIS2BOX_DATADIR`` represents the base
directory for all data managed in wis2box.

The default enviroment variables are below.

.. literalinclude:: ../../../../wis2box_example.env
   :language: bash
