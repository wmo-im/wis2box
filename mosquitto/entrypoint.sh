#!/bin/sh

echo "Setting mosquitto authentication"
mosquitto_passwd -b -c /mosquitto/config/password.txt $WIS2BOX_BROKER_USERNAME $WIS2BOX_BROKER_PASSWORD
mosquitto_passwd -b /mosquitto/config/password.txt everyone everyone

sed -i "s#_WIS2BOX_BROKER_QUEUE_MAX#$WIS2BOX_BROKER_QUEUE_MAX#" /mosquitto/config/mosquitto.conf
sed -i "s#_WIS2BOX_BROKER_USERNAME#$WIS2BOX_BROKER_USERNAME#" /mosquitto/config/acl.conf

/usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
