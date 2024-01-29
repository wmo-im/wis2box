The Dockerfile pins the keycloak image to a specific version because this is the version that
we have exported the JSON configuration from.

`wis2box-keycloak*` are legacy files which contain only the `wis2box` realm. Some of these may
be from an earlier export which sets up groups in the `wis2box` client.

`keycloak-secure.json` and `keycloak-insecure.json` are identical files containing exports
of both the `master` and `wis2box` realms where `sslRequired` has be set to false for both realms
in the insecure version.

NOTE:

As per https://howtodoinjava.com/devops/keycloak-script-upload-is-disabled/
We have removed the "authorizationSettings" node (and the previous trailing ',') from
`keycloak-*.json` because it contains a link to a JS file that keycloak will not import by default.
