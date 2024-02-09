#!/bin/bash
# entrypoint.sh

# wait

# Start Keycloak server with original parameters and redirect output to log file
/opt/keycloak/bin/kc.sh "$@" > /opt/keycloak/keycloak.log 2>&1 &

# set alias for kcadm
shopt -s expand_aliases
alias kcadm="/opt/keycloak/bin/kcadm.sh"

# login, wait for keycloak to start
while true; do
    output=$(kcadm config credentials --server http://keycloak:8080/oauth --realm master --user $KEYCLOAK_ADMIN --password $KEYCLOAK_ADMIN_PASSWORD 2>&1)
    echo $output
    if [[ ! $output == *"failed"* ]]; then
        break
    fi
    sleep 5
done

# set ssl required none
kcadm update realms/master -s sslRequired=NONE

# check if the realm exists, if not create it
realm_exists=$(kcadm get realms/wis2box 2>&1)
echo $realm_exists
if [[ $realm_exists == *"not found"* ]]; then
    # create wis2box realm
    echo "Realm wis2box does not exist. Creating."
    kcadm create realms -s realm=wis2box -s enabled=true
else
    # Realm already exists, handle accordingly (you may choose to update it or do nothing)
    echo "Realm wis2box already exists. Skipping creation."
fi
# set ssl required none
kcadm update realms/wis2box -s sslRequired=NONE

# check if the client exists, if not create it
client_exists=$(kcadm get clients -r wis2box --fields id,clientId | grep "\"wis2box\"" 2>&1)
if [[ ! $client_exists == *"wis2box"* ]]; then
    echo "Client wis2box does not exist. Creating."
    # create wis2box user in wis2box realm
    kcadm create clients -r wis2box -s clientId=wis2box -s enabled=true -s directAccessGrantsEnabled=true -s publicClient=false -s protocol=openid-connect
else
    # Client already exists, handle accordingly (you may choose to update it or do nothing)
    echo "Client wis2box already exists. Skipping creation."
fi

# get the client-id
CLIENT_ID=$(kcadm get clients -r wis2box --fields id,clientId | grep -B2 "\"wis2box\"" | grep "\"id\"" | cut -d\" -f4)

# Update the client access settings
kcadm update clients/$CLIENT_ID -r wis2box -s adminUrl=$WIS2BOX_URL/oauth
kcadm update clients/$CLIENT_ID -r wis2box -s baseUrl=$WIS2BOX_URL/wis2box-webapp
kcadm update clients/$CLIENT_ID -r wis2box -s webOrigins=\[\"+\"\]
kcadm update clients/$CLIENT_ID -r wis2box -s redirectUris=\[\"$WIS2BOX_URL/*\"\]

# reconnect containers'output to the log
tail -f /opt/keycloak/keycloak.log