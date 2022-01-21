FROM docker.elastic.co/elasticsearch/elasticsearch:7.16.2

ENV discovery.type=single-node
ENV node.name=elasticsearch-01
ENV discovery.seed_hosts=elasticsearch-01
ENV bootstrap.memory_lock=true
ENV ES_JAVA_OPTS="-Xms512m -Xmx512m"
