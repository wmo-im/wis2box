.. _installation:

Installation
============

wis2node is built with the intention of easy installation across operating systems and environments.

Requirements and dependencies
-----------------------------

wis2node runs on `Python 3 <https://www.python.org/downloads/>`_ and `Docker 1.13.0+ <https://docs.docker.com/get-docker/>`_.

Core dependencies are installed as containers in the docker compose deployment of wis2node. This is true for 
the software wis2node itself, which runs as a container orchestrating the necessary components of a node in the WIS network.

After Python and Docker are installed, wis2node needs to be installed. 

github
------

`wis2node github <https://github.com/wmo-im/wis2node>`_

.. code-block::

    git clone https://github.com/wmo-im/wis2node.git
    cd wis2node

ZIP Archive
-----------

`Download wis2node ZIP archive <https://github.com/wmo-im/wis2node/archive/refs/heads/main.zip>`_

.. code-block::

    # curl or any other tool
    curl https://github.com/wmo-im/wis2node/archive/refs/heads/main.zip
    cd wis2node-main

Summary
-------
Congratulations! Whichever of the abovementioned methods you chose, you have successfully installed wis2node
onto your system.
