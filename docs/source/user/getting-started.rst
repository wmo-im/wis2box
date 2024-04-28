.. _getting-started:

Getting started
===============

wis2box can be run on any Linux instance (bare metal or cloud hosted VM) with Python, Docker and Docker Compose installed. 
The recommended OS is Ubuntu 20.04 LTS.

.. note::

   wis2box may work on other operating systems (for example AlmaLinux or Windows), but the officially supported OS is Ubuntu.

When choosing the environment for the wis2box, consider the following:

* The wis2box instance should have suitable Internet connectivity, to download the required Docker images used in the wis2box stack
* In order for the wis2box instance to function as a WIS2 Node, HTTP and MQTT ports on the instance need to be accessible over the public Internet
* Ensure that the system providing input data can access the wis2box instance

.. note::
    
    Before exposing the wis2box to the Internet, please review the 'security considerations' section in the :ref:`public-services-setup` section. 

Network requirements
--------------------

The wis2box-software requires the following network ports to be available on the host system:

* 80/tcp (HTTP)
* 1883/tcp (MQTT)
* 3000/tcp (Grafana)
* 9000/tcp (MinIO)
* 9001/tcp (MinIO Console)

In order for the wis2box to be accessible from the Internet, the following ports on the host should be routed to a public IP address:

* 80/tcp (HTTP)
* 1883/tcp (MQTT)

It is recommended to use a reverse proxy (for example `NGINX`_) to provide HTTPS access to the wis2box.

System requirements
-------------------

System requirements depend on the amount of data ingested.  We recommend minimum 2 vCPUs with 4GB Memory and 24GB of local storage.

For example, the following Amazon AWS EC2 instance types have been utilized as part of various `wis2box demonstrations <https://demo.wis2box.wis.wmo.int>`_.

* 0 - 2000 observations per day: `t3a.medium` instance:

  * 2 vCPUs, x86_64 architecture, 4GB Memory, up to 5 Gigabit network, 24GB attached storage (~35 USD per month for on-demand Linux based OS)
* 2000 - 10000 observations per day: `t3a.large` instance:

  * 2 vCPUs, x86_64 architecture, 8GB Memory, up to 5 Gigabit network, 24GB attached storage (~70 USD per month for on-demand Linux based OS)

Software dependencies
---------------------

The services in wis2box are provided through a stack of `Docker`_ containers, which are configured using `Docker Compose`_. 

wis2box requires the following prior to installation:

.. csv-table::
   :header: Requirement,Version
   :align: left

   Python,3.8 or higher
   Docker Engine, 20.10.14 or higher
   Docker Compose, 2.0 or higher

The following commands be used to setup the required software on Ubuntu (20.04 LTS, 22.04 LTS) systems:

.. note::

   Execute the below commands one by one, and do not copy / paste the entire block

.. code-block:: bash
    
    sudo mkdir -m 0755 -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    sudo echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get -y update
    sudo apt-get install -y docker-ce docker-compose-plugin unzip python3-pip
    sudo pip3 install pip --upgrade
    sudo pip3 install pyopenssl --upgrade
    sudo pip3 install requests==2.26.0 urllib3==1.26.0

The following commands can be used to inspect the available versions of Python, Docker and Docker Compose on your system:

.. code-block:: bash

    docker version
    docker compose version
    python3 -V

The wis2box software should be run by system user that is part of the ``docker`` group.  
The following command can be used to add the current user to the ``docker`` group:	

.. code-block:: bash

    sudo usermod -aG docker $USER

Switch to this user and check that you can run docker hello-world:

.. code-block:: bash

    sudo su - $USER
    docker run hello-world

You should see the following output:

.. code-block:: bash

    Hello from Docker!
    This message shows that your installation appears to be working correctly.

    To generate this message, Docker took the following steps:
     1. The Docker client contacted the Docker daemon.
     2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
        (amd64)
     3. The Docker daemon created a new container from that image which runs the
        executable that produces the output you are currently reading.
     4. The Docker daemon streamed that output to the Docker client, which sent it
        to your terminal.

    (...)

Once you have verified these requirements, go to :ref:`setup` for a step-by-step guide to install and configure your wis2box.

.. _`Docker`: https://docs.docker.com/get-started/overview
.. _`Docker Compose`: https://github.com/docker/compose/releases
.. _`NGINX`: https://nginx.org
