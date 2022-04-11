.. _monitoring:

Monitoring
==========

wis2box has built-in monitoring functions based on prometheus, loki and grafana. The Grafana-endpoint is exposed on the localhost at port 3000.

Grafana uses two data-sources to display monitoring-data:
- prometheus: actively 'scrapes' data from the configured prometheus-client exporters every X seconds
- loki: logging end-point for the docker-containers that compose the wis2box

Prometheus exporters
--------------------
- metrics_collector: collects data on file-system
- mqtt_metric_collector: collects data on messages published, using an mqtt-session subscribed to the wis2box-broker

Loki logging
------------
The logs of the following docker-containers are sent to loki
- wis2box
- wis2box-ui
- 

Monitoring topics
-----------------

.. toctree::
   :maxdepth: 2

   grafana
   exploring-logs

