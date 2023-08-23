.. _monitoring:

Monitoring
==========

wis2box has built-in monitoring functions based on `Prometheus <https://prometheus.io/docs/introduction/overview/>`_, `Loki <https://grafana.com/docs/loki/latest/>`_ and `Grafana <https://grafana.com/docs/grafana/latest/>`_. 

The Grafana endpoint can be visualized at http://localhost/monitoring.

Grafana uses two data sources to display monitoring data:

- Prometheus: actively 'scrapes' data from the configured prometheus-client exporters every X seconds
- Loki: logging endpoint for the Docker containers that compose the wis2box

Prometheus exporters for wis2box
--------------------------------

The exporters for wis2box are based on the `Prometheus Python Client <https://github.com/prometheus/client_python>`_

- mqtt_metric_collector: collects data on messages published, using an mqtt-session subscribed to the wis2box-broker

wis2box also analyzes prometheus metrics from MinIO.

.. note::

   For more information see the `list of supported MinIO metrics <https://github.com/minio/minio/blob/master/docs/metrics/prometheus/list.md>`_

The default retention period for Prometheus metrics is 10 days.  This value can be modified in the Prometheus startup flag ``--storage.tsdb.retention.time`` in ``docker-compose.monitoring.yml``.

Loki logging
------------

The logs of the following Docker containers are sent to Loki:

- mosquitto
- mqp-publisher
- wis2box
- wis2box-api
- wis2box-auth
- wis2box-ui

The default retention period for Loki logs is 10 days. 
This value can be modified in the Loki configuration at ``loki/loki-config.yml``. 

Monitoring topics
-----------------

.. toctree::
   :maxdepth: 2

   grafana
   exploring-logs
