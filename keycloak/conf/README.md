`keycloak-secure.json` and `keycloak-insecure.json` are identical files containing exports
of both the `master` and `wis2box` realms where `sslRequired` has be set to `non`` for both realms
in the insecure version and left as `external` in the secure version.

NOTES
- As per https://howtodoinjava.com/devops/keycloak-script-upload-is-disabled/
  We have removed the "authorizationSettings" node (and the previous trailing ',') from
  `keycloak-*.json` because it contains a link to a JS file that keycloak will not import
  by default.
- It was also necessary to manually remove the admin user (by setting) `"users": [ ]`
  so that admin can be created for `KEYCLOAK_ADMIN`, `KEYCLOAK_ADMIN_PASSWORD`
