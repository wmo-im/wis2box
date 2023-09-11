# WIP-FIXME: use envsubst to replace hardcoded http://localhost:8180/

location = /login {
    return 302 /oauth2/start?rd=$scheme://$host;
}

location = /logout {
    # Internally redirect to the signout endpoint of oauth2-proxy and also signout of keycloak
    proxy_pass http://keycloak:4180/oauth2/sign_out?rd=http://localhost:8180/realms/wis2box/protocol/openid-connect/logout;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Scheme $scheme;
}

location = /auth {
    # We use auth_request with oauth2-proxy in order to add X-User, X-Email and X-Group headers
    # see `protect-location.inc` for example use.
    internal;
    auth_request /oauth2/auth;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_set_header X-Original-URI $request_uri;

    # Handle 200 OK and 401 Unauthorized responses
    # In both cases we defer to wis2box-auth to actually authorize requests
    proxy_pass http://wis2box-auth:80/authorize;  # oauth2-proxy has added headers (authenticated user)
    error_page 401 = /authorize;  # no additional headers have been added (anonymous user)
}

location = /authorize {
    internal;
    proxy_pass http://wis2box-auth:80/authorize;
    proxy_pass_request_body off;
    proxy_set_header        Content-Length "";
    proxy_set_header        X-Original-URI $request_uri;
    proxy_set_header        Authorization $http_authorization;
    proxy_pass_header       Authorization;
}

# ----------------------------------------------------
# The configuration below is taken directly from
# https://oauth2-proxy.github.io/oauth2-proxy/docs/configuration/overview#configuring-for-use-with-the-nginx-auth_request-directive
# See also: https://oauth2-proxy.github.io/oauth2-proxy/docs/features/endpoints/

location /oauth2/ {
    proxy_pass       http://keycloak:4180;
    proxy_set_header Host                    $host;
    proxy_set_header X-Real-IP               $remote_addr;
    proxy_set_header X-Scheme                $scheme;
    proxy_set_header X-Auth-Request-Redirect $request_uri;
    # or, if you are handling multiple domains:
    # proxy_set_header X-Auth-Request-Redirect $scheme://$host$request_uri;
}

location = /oauth2/auth {
    proxy_pass       http://keycloak:4180;
    proxy_set_header Host             $host;
    proxy_set_header X-Real-IP        $remote_addr;
    proxy_set_header X-Scheme         $scheme;
    # nginx auth_request includes headers but not body
    proxy_set_header Content-Length   "";
    proxy_pass_request_body           off;
}
