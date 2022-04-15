.. _monitoring:

Monitoring
==========

wis2box has built-in monitoring functions based on `prometheus <https://prometheus.io/docs/introduction/overview/>`_, `loki <https://grafana.com/docs/loki/latest/>`_ and `grafana <https://grafana.com/docs/grafana/latest/>`_. 
The Grafana-endpoint is exposed on the localhost at port 3000.
Go to http://localhost:3000 to see the home dashboard of wis2box once the stack is running. 

Grafana uses two data-sources to display monitoring-data:
- prometheus: actively 'scrapes' data from the configured prometheus-client exporters every X seconds
- loki: logging end-point for the docker-containers that compose the wis2box

Prometheus exporters for wis2box
--------------------

The exporters for wis2box are based on the `Prometheus Python Client <https://github.com/prometheus/client_python>`_

- metrics_collector: collects data on file-system
- mqtt_metric_collector: collects data on messages published, using an mqtt-session subscribed to the wis2box-broker

Loki logging
------------
The logs of the following docker-containers are sent to loki
- data-consumer
- mqp-publisher
- wis2box
- wis2box-ui
- mosquitto
- wis2box-api
- wis2box-auth

Monitoring topics
-----------------

.. toctree::
   :maxdepth: 2

   grafana
   exploring-logs

