## Keycloak manual configuration

The following instructions describe how to manually configure keycloak by creating a realm and client, where:

- A realm is an isolated environment within Keycloak for managing users, roles, and authentication and authorization settings for a specific set of applications or services.
- A client represents an application or service that is secured by Keycloak and is configured to use Keycloak for authentication and authorization.

These instructions are temporary. The required realm and client will be imported/created automatically when the container is built, leaving only the creation and management of users and groups.

## Creating a realm

- Visit KeyCloak admin console in the browser: `${WIS2BOX_URL}:8180/admin` 
- Log into the `master` (default) realm using the `KEYCLOAK_ADMIN` and `KEYCLOAK_ADMIN_PASSWORD` credentials that you created in your `wis2box.env`
- Select the down arrow of the 'Realm selector' drop down in the top left and click <kbd>Create Realm</kbd>
- Enter `wis2box` as realm name and click <kbd>Create</kbd>

## Creating a client

- In the KeyCloak admin console, select with `wis2box` realm and click on the `Clients` section of the manage menu
- Click the <kdb>Create client</kbd> button
- On the `Create client` page, keep the `Client type` as `OpenID Connect` and enter a `Client ID` (e.g. `wis2box`)
- After clicking <kbd>Next</kbd>, set `Client authentication` to `On` and `Authorization` to `On` and click <kbd>Save</kbd>
  - After creating the client the `Settings` tab of the `client details` page is shown, this can also be accessed by returning to the `Clients` section of the manage menu and choosing the new `wis2box` client
  - In the `Settings` tab:
      - set the `Valid redirect URIs` (for the client) to the value of `${WIS2BOX_URL}/*` and `Valid post logout redirect URIs` to `+` (to use the same value as the `Valid redirect URIs`)
  - In the `Credentials` tab copy the `Client secret` and paste into the `client_secret` property in `client_secrets.json`