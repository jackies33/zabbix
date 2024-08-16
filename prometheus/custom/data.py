


hosts_ports_tcp = [

    #gateway_proxy_loadbalancer services
    #kr01
    ('10.50.52.193', 80, 'tcp', 'kr01-zbx-net-alb01', 'haproxy-zbx'),
    ('10.50.52.194', 80, 'tcp', 'kr01-zbx-net-alb01', 'haproxy-grf'),
    ('10.50.52.195', 80, 'tcp', 'kr01-zbx-net-alb01', 'haproxy-grlg'),
    ('10.50.52.193', 443, 'tcp', 'kr01-zbx-net-alb01', 'haproxy-zbx'),
    ('10.50.52.194', 443, 'tcp', 'kr01-zbx-net-alb01', 'haproxy-grf'),
    ('10.50.52.195', 443, 'tcp', 'kr01-zbx-net-alb01', 'haproxy-grlg'),
    ('10.50.52.196', 5672, 'tcp', 'kr01-zbx-net-alb01', 'haproxy-rabbitmq'),
    ('10.50.52.196', 5005, 'tcp', 'kr01-zbx-net-alb01', 'haproxy-rbq_proxy'),
    ('10.50.174.33', 179, 'tcp', 'kr01-zbx-net-alb01', 'bird'),
    ('10.50.164.33', 179, 'tcp', 'sdc-zbx-net-alb02', 'bird'),
    ('10.50.174.38', 5000, 'tcp', 'kr01-zbx-lb01', 'haproxy-psql'),
    ('10.50.174.38', 5001, 'tcp', 'kr01-zbx-lb01', 'haproxy-psql'),
    ('10.50.174.1', 179, 'tcp', 'kr01-net-aaa-alb01', 'bird'),
    ('10.50.174.1', 7777, 'tcp', 'kr01-net-aaa-alb01', 'LinOTP_Docker'),
    ('10.50.174.1', 8888, 'tcp', 'kr01-net-aaa-alb01', 'OpenWisp_Docker'),
    ('10.50.164.5', 5000, 'tcp', 'kr01-net-aaa-lb01', 'haproxy-psql'),
    ('10.50.164.5', 5001, 'tcp', 'kr01-net-aaa-lb01', 'haproxy-psql'),
    ('10.50.164.5', 7000, 'tcp', 'kr01-net-aaa-lb01', 'haproxy-http'),

    #sdc
    ('10.50.52.193', 80, 'tcp', 'sdc-zbx-net-alb02', 'haproxy-zbx'),
    ('10.50.52.194', 80, 'tcp', 'sdc-zbx-net-alb02', 'haproxy-grf'),
    ('10.50.52.195', 80, 'tcp', 'sdc-zbx-net-alb02', 'haproxy-grlg'),
    ('10.50.52.193', 443, 'tcp', 'sdc-zbx-net-alb02', 'haproxy-zbx'),
    ('10.50.52.194', 443, 'tcp', 'sdc-zbx-net-alb02', 'haproxy-grf'),
    ('10.50.52.195', 443, 'tcp', 'sdc-zbx-net-alb02', 'haproxy-grlg'),
    ('10.50.52.196', 5672, 'tcp', 'sdc-zbx-net-alb02', 'haproxy-rabbitmq'),
    ('10.50.52.196', 5005, 'tcp', 'sdc-zbx-net-alb02', 'haproxy-rbq_proxy'),
    ('10.50.164.38', 5000, 'tcp', 'sdc-zbx-lb02', 'haproxy-psql'),
    ('10.50.164.38', 5001, 'tcp', 'sdc-zbx-lb02', 'haproxy-psql'),
    ('10.50.164.1', 179, 'tcp', 'sdc01-net-aaa-alb01', 'bird'),
    ('10.50.164.1', 7777, 'tcp', 'sdc01-net-aaa-alb01', 'LinOTP_Docker'),
    ('10.50.164.1', 8888, 'tcp', 'sdc01-net-aaa-alb01', 'OpenWisp_Docker'),
    ('10.50.164.5', 5000, 'tcp', 'sdc01-net-aaa-lb01', 'haproxy-psql'),
    ('10.50.164.5', 5001, 'tcp', 'sdc01-net-aaa-lb01', 'haproxy-psql'),
    ('10.50.164.5', 7000, 'tcp', 'sdc01-net-aaa-lb01', 'haproxy-http'),

    #test

    #graylog services
    ('10.50.174.39', 9000, 'tcp', 'kr01-net-log-graylog01', 'graylog'),
    ('10.50.174.40', 9000, 'tcp', 'kr01-net-log-graylog02', 'graylog'),
    ('10.50.164.39', 9000, 'tcp', 'sdc-net-log-graylog01', 'graylog'),
    ('10.50.164.40', 9000, 'tcp', 'sdc-net-log-graylog02', 'graylog'),

    #mongodb nodes
    ('10.50.174.41', 27017, 'tcp', 'kr01-net-log-mongodb01', 'mongodb'),
    ('10.50.164.41', 27017, 'tcp', 'sdc-net-log-mongodb01', 'mongodb'),
    ('10.50.194.33', 27017, 'tcp', 'm9-zbx-etcd01', 'mongodb'),
    ('10.50.74.171', 27017, 'tcp', 'kr01-main-noc', 'mongodb'),

    #opensearch services
    ('10.50.174.42', 9200, 'tcp', 'kr01-net-log-opensearch01', 'opensearch'),
    ('10.50.164.42', 9200, 'tcp', 'sdc-net-log-opensearch01', 'opensearch'),
    ('10.50.194.33', 9200, 'tcp', 'm9-zbx-etcd01', 'opensearch'),

    #postgresqldb services
    ('10.50.174.35', 8008, 'tcp', 'kr01-zbx-db01', 'patroni'),
    ('10.50.174.35', 5432, 'tcp', 'kr01-zbx-db01', 'postgresql'),
    ('10.50.164.35', 8008, 'tcp', 'sdc-zbx-db02', 'patroni'),
    ('10.50.164.35', 5432, 'tcp', 'sdc-zbx-db02', 'postgresql'),
    ('10.50.74.98', 5432, 'tcp', 'netbox-dev', 'postgresql'),
    ('10.50.164.6', 5432, 'tcp', 'sdc01-net-aaa-pgdb01', 'postgresql'),
    ('10.50.174.6', 5432, 'tcp', 'kr01-net-aaa-pgdb01 ', 'postgresql'),



    #grafana services
    ('10.50.174.36', 3000, 'tcp', 'kr01-zbx-grafana01', 'grafana'),
    ('10.50.164.36', 3000, 'tcp', 'sdc-zbx-grafana02', 'grafana'),


    #zbx-server services
    ('10.50.174.34', 80, 'tcp', 'kr01-zbx-server01', 'nginx-zbx-web'),
    ('10.50.174.34', 8055, 'tcp', 'kr01-zbx-server01', 'zbx_consumer'),
    ('10.50.174.34', 10051, 'tcp', 'kr01-zbx-server01', 'zbx-trapper'),
    ('10.50.164.34', 80, 'tcp', 'sdc-zbx-server02', 'nginx-zbx-web'),
    ('10.50.164.34', 8055, 'tcp', 'sdc-zbx-server02', 'zbx_consumer'),
    ('10.50.164.34', 10051, 'tcp', 'sdc-zbx-server02', 'zbx-trapper'),
    ('10.50.174.37', 10051, 'tcp', 'kr01-zbx-proxy01', 'zbx-trapper'),
    ('10.50.164.37', 10051, 'tcp', 'sdc-zbx-proxy01', 'zbx-trapper'),

    #etcd services
    ('10.50.194.33', 2379, 'tcp', 'm9-zbx-etcd01', 'etcd'),
    ('10.50.194.33', 2380, 'tcp', 'm9-zbx-etcd01', 'etcd'),
    ('10.50.174.35', 2379, 'tcp', 'kr01-zbx-db01', 'etcd'),
    ('10.50.174.35', 2380, 'tcp', 'kr01-zbx-db01', 'etcd'),
    ('10.50.164.35', 2379, 'tcp', 'sdc-zbx-db02', 'etcd'),
    ('10.50.164.35', 2380, 'tcp', 'sdc-zbx-db02', 'etcd'),
    ('10.50.164.7', 2379, 'tcp', 'sdc01-net-aaa-etcd01', 'etcd'),
    ('10.50.164.7', 2380, 'tcp', 'sdc01-net-aaa-etcd01', 'etcd'),
    ('10.50.174.7', 2379, 'tcp', 'kr01-net-aaa-etcd01', 'etcd'),
    ('10.50.174.7', 2380, 'tcp', 'kr01-net-aaa-etcd01', 'etcd'),
    ('10.50.194.1', 2379, 'tcp', 'm9-net-aaa-etcd01', 'etcd'),
    ('10.50.194.1', 2380, 'tcp', 'm9-net-aaa-etcd01', 'etcd'),


    #netbox services
    ('10.50.74.98', 80, 'tcp', 'netbox-dev', 'netbox-web'),
    ('10.50.74.98', 443, 'tcp', 'netbox-dev', 'netbox-web'),

    #noc services
    ('10.50.74.171', 8123, 'tcp', 'kr01-main-noc', 'clickhouse'),
    ('10.50.74.171', 9292, 'tcp', 'kr01-main-noc', 'liftbridge'),
    ('10.50.74.171', 8300, 'tcp', 'kr01-main-noc', 'consul'),
    ('10.50.74.171', 3501, 'tcp', 'kr01-main-noc', 'web_remote_integration'),
    ('10.50.74.171', 80, 'tcp', 'kr01-main-noc', 'nginx_noc_web'),
    ('10.50.74.171', 443, 'tcp', 'kr01-main-noc', 'nginx_noc_web'),

    #RabbitMQ services
    ('10.50.174.43', 25672, 'tcp', 'kr01-net-sys-rbmq01', 'rabbitmq'),
    ('10.50.174.43', 15672, 'tcp', 'kr01-net-sys-rbmq01', 'rabbitmq'),
    ('10.50.174.43', 5672, 'tcp', 'kr01-net-sys-rbmq01', 'rabbitmq'),
    ('10.50.174.43', 5005, 'tcp', 'kr01-net-sys-rbmq01', 'rbq_proxy'),
    ('10.50.164.43', 25672, 'tcp', 'sdc-net-sys-rbmq02', 'rabbitmq'),
    ('10.50.164.43', 15672, 'tcp', 'sdc-net-sys-rbmq02', 'rabbitmq'),
    ('10.50.164.43', 5672, 'tcp', 'sdc-net-sys-rbmq02', 'rabbitmq'),
    ('10.50.164.43', 5005, 'tcp', 'sdc-net-sys-rbmq02', 'rbq_proxy'),

    #AAA Services
    #kr01
    ('10.50.174.2', 80, 'tcp', 'kr01-net-aaa-k8s-master01', 'LinOTP'),
    ('10.50.174.2', 8888, 'tcp', 'kr01-net-aaa-k8s-master01', 'OpenWisp'),
    ('10.50.174.3', 80, 'tcp', 'kr01-net-aaa-k8s-worker01', 'LinOTP'),
    ('10.50.174.3', 8888, 'tcp', 'kr01-net-aaa-k8s-worker01', 'OpenWisp'),
    ('10.50.174.4', 80, 'tcp', 'kr01-net-aaa-k8s-worker02', 'LinOTP'),
    ('10.50.174.4', 8888, 'tcp', 'kr01-net-aaa-k8s-worker02', 'OpenWisp'),
    ('10.50.174.8', 9000, 'tcp', 'kr01-net-aaa-logs01', 'GrayLog'),

    #sdc
    ('10.50.164.2', 80, 'tcp', 'sdс01-net-aaa-k8s-master01', 'LinOTP'),
    ('10.50.164.2', 8888, 'tcp', 'sdс01-net-aaa-k8s-master01', 'OpenWisp'),
    ('10.50.164.3', 80, 'tcp', 'sdc01-net-aaa-k8s-worker01', 'LinOTP'),
    ('10.50.164.3', 8888, 'tcp', 'sdc01-net-aaa-k8s-worker01', 'OpenWisp'),
    ('10.50.164.4', 80, 'tcp', 'sdc01-net-aaa-k8s-worker02', 'LinOTP'),
    ('10.50.164.4', 8888, 'tcp', 'sdc01-net-aaa-k8s-worker02', 'OpenWisp'),
    ('10.50.164.8', 5000, 'tcp', 'sdc01-net-aaa-registry01', 'DockerRegistry'),

    #AlarmManagment
    ('10.50.174.37', 8055, 'tcp', 'kr01-zbx-proxy01', 'zbx_alarm_logic'),
    ('10.50.164.37', 8055, 'tcp', 'sdc-zbx-proxy02', 'zbx_alarm_logic'),
    ('10.50.174.37', 8056, 'tcp', 'kr01-zbx-proxy01', 'zbx_sender'),
    ('10.50.164.37', 8056, 'tcp', 'sdc-zbx-proxy02', 'zbx_sender'),
    ('10.50.174.37', 8057, 'tcp', 'kr01-zbx-proxy01', 'zbx_deleter_short_alarms'),
    ('10.50.164.37', 8057, 'tcp', 'sdc-zbx-proxy02', 'zbx_deleter_short_alarms'),

    #prometheus services
    ('10.50.174.36', 9090, 'tcp', 'kr01-zbx-grafana01', 'prometheus'),
    ('10.50.164.36', 9090, 'tcp', 'sdc-zbx-grafana02', 'prometheus'),
    #nodeexporter prometheus
    ('10.50.174.33', 9100, 'tcp', 'kr01-zbx-net-alb01', 'node_exporter-prometheus'),
    ('10.50.194.33', 9100, 'tcp', 'm9-zbx-etcd01', 'node_exporter-prometheus'),
    ('10.50.164.41', 9100, 'tcp', 'sdc-net-log-mongodb01', 'node_exporter-prometheus'),
    ('10.50.174.41', 9100, 'tcp', 'kr01-net-log-mongodb01', 'node_exporter-prometheus'),
    ('10.50.164.33', 9100, 'tcp', 'sdc-zbx-net-alb02', 'node_exporter-prometheus'),
    ('10.50.174.39', 9100, 'tcp', 'kr01-net-log-graylog01', 'node_exporter-prometheus'),
    ('10.50.174.40', 9100, 'tcp', 'kr01-net-log-graylog02', 'node_exporter-prometheus'),
    ('10.50.164.39', 9100, 'tcp', 'sdc-net-log-graylog01', 'node_exporter-prometheus'),
    ('10.50.164.40', 9100, 'tcp', 'sdc-net-log-graylog02', 'node_exporter-prometheus'),
    ('10.50.174.42', 9100, 'tcp', 'kr01-net-log-opensearch01', 'node_exporter-prometheus'),
    ('10.50.164.42', 9100, 'tcp', 'sdc-net-log-opensearch01', 'node_exporter-prometheus'),
    ('10.50.174.35', 9100, 'tcp', 'kr01-zbx-db01', 'node_exporter-prometheus'),
    ('10.50.164.35', 9100, 'tcp', 'sdc-zbx-db02', 'node_exporter-prometheus'),
    ('10.50.174.36', 9100, 'tcp', 'kr01-zbx-grafana01', 'node_exporter-prometheus'),
    ('10.50.164.36', 9100, 'tcp', 'sdc-zbx-grafana02', 'node_exporter-prometheus'),
    ('10.50.174.38', 9100, 'tcp', 'kr01-zbx-lb01', 'node_exporter-prometheus'),
    ('10.50.164.38', 9100, 'tcp', 'sdc-zbx-lb02', 'node_exporter-prometheus'),
    ('10.50.174.37', 9100, 'tcp', 'kr01-zbx-proxy01', 'node_exporter-prometheus'),
    ('10.50.164.37', 9100, 'tcp', 'sdc-zbx-proxy01', 'node_exporter-prometheus'),
    ('10.50.174.34', 9100, 'tcp', 'kr01-zbx-server01', 'node_exporter-prometheus'),
    ('10.50.164.34', 9100, 'tcp', 'sdc-zbx-server02', 'node_exporter-prometheus'),
    ('10.50.74.98', 9100, 'tcp', 'netbox-dev', 'node_exporter-prometheus'),
    ('10.50.74.171', 9100, 'tcp', 'kr01-main-noc', 'node_exporter-prometheus'),
    ('10.50.174.43', 9100, 'tcp', 'kr01-net-sys-rbmq01', 'node_exporter-prometheus'),
    ('10.50.164.43', 9100, 'tcp', 'sdc-net-sys-rbmq02', 'node_exporter-prometheus'),
    ('10.50.164.1', 9100, 'tcp', 'sdc01-net-aaa-alb01', 'node_exporter-prometheus'),
    ('10.50.164.2', 9100, 'tcp', 'sdс01-net-aaa-k8s-master01', 'node_exporter-prometheus'),
    ('10.50.164.3', 9100, 'tcp', 'sdc01-net-aaa-k8s-worker01', 'node_exporter-prometheus'),
    ('10.50.164.4', 9100, 'tcp', 'sdc01-net-aaa-k8s-worker02', 'node_exporter-prometheus'),
    ('10.50.164.5', 9100, 'tcp', 'sdc01-net-aaa-lb01', 'node_exporter-prometheus'),
    ('10.50.164.6', 9100, 'tcp', 'sdc01-net-aaa-pgdb01', 'node_exporter-prometheus'),
    ('10.50.164.7', 9100, 'tcp', 'sdc01-net-aaa-etcd01', 'node_exporter-prometheus'),
    ('10.50.164.8', 9100, 'tcp', 'sdc01-net-aaa-registry01', 'node_exporter-prometheus'),
    ('10.50.164.9', 9100, 'tcp', 'sdc01-net-aaa-mon01', 'node_exporter-prometheus'),
    ('10.50.174.1', 9100, 'tcp', 'kr01-net-aaa-alb01', 'node_exporter-prometheus'),
    ('10.50.174.2', 9100, 'tcp', 'kr01-net-aaa-k8s-master01', 'node_exporter-prometheus'),
    ('10.50.174.3', 9100, 'tcp', 'kr01-net-aaa-k8s-worker01', 'node_exporter-prometheus'),
    ('10.50.174.4', 9100, 'tcp', 'kr01-net-aaa-k8s-worker02', 'node_exporter-prometheus'),
    ('10.50.174.5', 9100, 'tcp', 'kr01-net-aaa-lb01', 'node_exporter-prometheus'),
    ('10.50.174.6', 9100, 'tcp', 'kr01-net-aaa-pgdb01', 'node_exporter-prometheus'),
    ('10.50.174.7', 9100, 'tcp', 'kr01-net-aaa-etcd01', 'node_exporter-prometheus'),
    ('10.50.174.8', 9100, 'tcp', 'kr01-net-aaa-logs01', 'node_exporter-prometheus'),
    ('10.50.174.9', 9100, 'tcp', 'kr01-net-aaa-mon01', 'node_exporter-prometheus'),
    ('10.50.194.1', 9100, 'tcp', 'm9-net-aaa-etcd011 ', 'node_exporter-prometheus'),


]

hosts_ports_udp = [

    #monitoring_kr01
    ('10.50.52.195', 514, 'udp', 'kr01-zbx-net-alb01', 'proxy-syslog-grlg','10.50.174.33'),
    ('10.50.174.39', 514, 'udp', 'kr01-net-log-graylog01', 'syslog-grlg','10.50.174.39'),
    ('10.50.174.40', 514, 'udp', 'kr01-net-log-graylog02', 'syslog-grlg','10.50.174.40'),

    #monitoring_sdc
    ('10.50.52.195', 514, 'udp', 'sdc-zbx-net-alb02', 'proxy-syslog-grlg', '10.50.164.33'),
    ('10.50.164.39', 514, 'udp', 'sdc-net-log-graylog01', 'syslog-grlg', '10.50.164.39'),
    ('10.50.164.40', 514, 'udp', 'sdc-net-log-graylog02', 'syslog-grlg', '10.50.164.40'),

    #AAA
    #kr01
    ('10.50.52.192', 1812, 'udp', 'kr01-net-aaa-alb01', 'proxy-radius', '10.50.174.1'),
    #('10.50.174.2', 1815, 'udp', 'kr0101-net-aaa-k8s-master01', 'radius', '10.50.174.2'),
    #('10.50.174.3', 1815, 'udp', 'kr0101-net-aaa-k8s-worker01', 'radius', '10.50.174.3'),
    #('10.50.174.4', 1815, 'udp', 'kr0101-net-aaa-k8s-worker02', 'radius', '10.50.174.4'),
    #sdc
    ('10.50.52.192', 1812, 'udp', 'sdc01-net-aaa-alb01', 'proxy-radius', '10.50.164.1'),
    #('10.50.164.2', 1815, 'udp', 'sdс01-net-aaa-k8s-master01', 'radius', '10.50.164.2'),
    #('10.50.164.3', 1815, 'udp', 'sdc01-net-aaa-k8s-worker01', 'radius', '10.50.164.3'),
    #('10.50.164.4', 1815, 'udp', 'sdc01-net-aaa-k8s-worker02', 'radius', '10.50.164.4'),

    # ('10.50.174.34', 161, 'udp', 'kr01-zbx-server01', 'snmpd'),
    # ('10.50.164.34', 161, 'udp', 'sdc-zbx-server02', 'snmpd'),


]

prometheus_file = '/opt/prometheus/node_exporter-1.2.2.linux-amd64/textfile/ports_status.prom'

pyusername = 'pyadmin'
password_pyadmin = 'jjbfVU4hh#$*^VFV5573vFGHVDvCF@'


