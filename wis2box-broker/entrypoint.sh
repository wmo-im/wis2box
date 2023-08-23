#!/bin/sh

if [ -f /tmp/wis2box.crt ]; then
    echo "SSL enabled"
    echo "setup /mosquitto/certs"
    mkdir -p /mosquitto/certs
    cp /tmp/wis2box.crt /mosquitto/certs
    cp /tmp/wis2box.key /mosquitto/certs
    chown -R mosquitto:mosquitto /mosquitto/certs
    cp -f /mosquitto/config/mosquitto-ssl.conf /mosquitto/config/mosquitto.conf
else
    echo "SSL disabled"
fi

echo "Setting mosquitto authentication"
if [ ! -e "/mosquitto/config/password.txt" ]; then
    echo "Adding wis2box users to mosquitto password file"
    mosquitto_passwd -b -c /mosquitto/config/password.txt $WIS2BOX_BROKER_USERNAME $WIS2BOX_BROKER_PASSWORD
    mosquitto_passwd -b /mosquitto/config/password.txt everyone everyone
else
    echo "Mosquitto password file already exists. Skipping wis2box user addition."
fi

sed -i "s#_WIS2BOX_BROKER_QUEUE_MAX#$WIS2BOX_BROKER_QUEUE_MAX#" /mosquitto/config/mosquitto.conf
sed -i "s#_WIS2BOX_BROKER_USERNAME#$WIS2BOX_BROKER_USERNAME#" /mosquitto/config/acl.conf

/usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
