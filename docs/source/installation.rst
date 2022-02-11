.. _installation:

Installation
============

wis2node is built for easy installation across various operating systems and environments.

Requirements and dependencies
-----------------------------

wis2node requires `Python`_ 3 and `Docker`_ 1.13.

Core dependencies are installed as containers in the Docker Compose deployment of wis2node. This
is true for the software wis2node itself, which runs as a container orchestrating the necessary
data management workflows of a node as part of the WIS 2.0 network.

Once Python and Docker are installed, wis2node needs to be installed. 

ZIP Archive
-----------

.. code-block:: bash

    # curl, wget or download from your web browser 
    curl https://github.com/wmo-im/wis2node/archive/refs/heads/main.zip
    cd wis2node-main

GitHub
------

.. code-block:: bash

    # clone wis2node GitHub repository
    git clone https://github.com/wmo-im/wis2node.git
    cd wis2node


Summary
-------

Congratulations! Whichever of the abovementioned methods you chose, you have successfully installed wis2node
onto your system. From here, you can get started with test data by following the :ref:`quickstart`, or continue on to 
:ref:`configuration`.

.. _`Python`: https://www.python.org/downloads
.. _`Docker`: https://docs.docker.com/get-docker
