The Dockerfile pins the keycloak image to a specific version because this is the version that
we have exported the JSON configuration from.

wis2box-keycloak-secure.json is the orginal export (with the default `sslRequired="external"`).
wis2box-keycloak-secure.json is identical but with `sslRequired="none"`.

These configuration files were created from an earlier export which sets up groups in the
`wis2box` client. Also see `wis2box-keycloak-basic.json` for an exported configuration which only
defines up the realm and client without further setup.
