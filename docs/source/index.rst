======================
What is WIS2 in a box?
======================

WIS2 in a box (wis2box) is a **Reference Implementation of a WIS2 Node**.
It is developed and supported by WMO Secretariat and Members to **help accelerate the implementation of WIS 2.0**.

wis2box was designed to be to be **cost-effective** and **low-barrier** to operate, to enable any WMO Member to publish and receive internationally exchanged weather data.

**wis2box is Free and Open Source** and released under the `Apache License <https://docs.wis2box.wis.wmo.int/en/latest/community/license.html>`_

wis2box consists of multiple software packages that provide all services required to run a WIS2 Node, namely:

- `github.com/wmo-im/wis2box <https://github.com/wmo-im/wis2box>`_ Core services to publish WIS2 Discovery Metadata and  Notification Messages
- `github.com/wmo-im/wis2box-api <https://github.com/wmo-im/wis2box-api>`_  Application Programming Interface that provides an OGC API to discover, access, and visualize notifications, data -collections and configuration (datasets, stations) and which provides support for data handling of WMO encodings and formats
- `github.com/wmo-im/wis2box-ui <https://github.com/wmo-im/wis2box-ui>`_ User interface to display datasets and provide visualizations for ingested data
- `github.com/wmo-im/wis2box-webapp <https://github.com/wmo-im/wis2box-webappp>`_ Web -application to interactively configure wis2box and monitor published data
- `github.com/wmo-im/wis2box-auth <https://github.com/wmo-im/wis2box-auth>`_ Access control functionality to datasets exposed via wis2box and to apply authentication API services used by wis2box-webapp
- `github.com/wmo-im/wis2downloader <https://github.com/wmo-im/wis2downloader>`_ Subscription and download capability for access to data published by other WIS2 Nodes

**WIS2 in a box is released using a Deployment Bundle that simplifies the setup of a WIS2 Node by providing all required services as Docker containers.**

The release archive consists of a set of Docker Compose files and Python scripts, referencing pre-built Docker images stored in the wis2box software repositories on GitHub

In addition to the wis2box software packages mentioned above, wis2box  leverages the following Free and Open Source Software (FOSS):

- storage using `MinIO <https://min.io/docs/minio/container/index.html>`_
- MQTT broker using `mosquitto <https://mosquitto.org/>`_ 
- Web proxy using `nginx <https://nginx.org/en/>`_
- `OGC API <https://ogcapi.ogc.org/>`_ capability using `pygeoapi <https://pygeoapi.io/>`_
- API backend using `Elasticsearch <https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html>`_
- Monitoring dashboards using `Grafana <https://grafana.com/docs/grafana/latest/setup-grafana/configure-docker/>`_	
- Metrics collection using `Prometheus <https://prometheus.io/>`_
- Log storage using `Loki <https://grafana.com/docs/loki/latest/setup/install/docker/>`_	
- WMO format encoding/decoding using `ecCodes <https://confluence.ecmwf.int/display/ECC>`_ 

Requirements to run a WIS2 Node using the wis2box deployment bundle:

1.	**Host instance that is routed to the public Internet**, hosted in the cloud or in a high-performance on-premise data-centre
2.	**Host OS using Ubuntu with Python, Docker and Docker Compose pre-installed**

Please follow :ref:`getting-started` for more information on the host-requirements and to start running a WIS2 Node using the wis2box deployment bundle.

User guide
==========

The user guide provides step-by-step instructions to start running a WIS2 Node using the wis2box deployment bundle.

.. toctree::
   :maxdepth: 1
   :caption: User guide
   :name: toc-user

   user/getting-started
   user/setup
   user/data-ingest
   user/gts-headers-in-wis2
   user/public-services-setup
   user/downloading-data
   user/cap-alerts

Reference guide
===============

The reference documentation is more complete and programmatic in nature.  It contains a comprehensive set
of information on wis2box for easy reference.

.. toctree::
   :maxdepth: 1
   :caption: Reference guide
   :name: toc-reference

   reference/wis2
   reference/how-wis2box-works
   reference/configuration
   reference/administration
   reference/quickstart
   reference/running/index
   reference/storage
   reference/monitoring/index
   reference/services
   reference/auth
   reference/data-access/index
   reference/development
   reference/extending-wis2box

Community
=========

The community documentation provides information on where to find support and how to contribute to wis2box.

.. toctree::
   :maxdepth: 1
   :caption: Community
   :name: toc-community

   community/support
   community/troubleshooting
   community/contributing
   community/license
