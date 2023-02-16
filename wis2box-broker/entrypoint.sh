#!/bin/sh

if [ -f /tmp/wis2box.crt ]; then
    echo "SSL enabled"
    echo "setup /mosquitto/certs"
    mkdir -p /mosquitto/certs
    cp /tmp/wis2box.crt /mosquitto/certs
    cp /tmp/wis2box.key /mosquitto/certs
    chown -R mosquitto:mosquitto /mosquitto/certs
    cp /mosquitto/config/mosquitto-ssl.conf /mosquitto/config/mosquitto.conf
else
    echo "SSL disabled"
    cp /mosquitto/config/mosquitto-nossl.conf /mosquitto/config/mosquitto.conf
fi

echo "Setting mosquitto authentication"
mosquitto_passwd -b -c /mosquitto/config/password.txt $WIS2BOX_BROKER_USERNAME $WIS2BOX_BROKER_PASSWORD
mosquitto_passwd -b /mosquitto/config/password.txt everyone everyone

sed -i "s#_WIS2BOX_BROKER_QUEUE_MAX#$WIS2BOX_BROKER_QUEUE_MAX#" /mosquitto/config/mosquitto.conf
sed -i "s#_WIS2BOX_BROKER_USERNAME#$WIS2BOX_BROKER_USERNAME#" /mosquitto/config/acl.conf

/usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
