# Sanitize original request headers to remove any claims originating externally
proxy_set_header X-User   "";
proxy_set_header X-Email  "";
proxy_set_header X-Groups "";

auth_request /auth;

# Set X-User, X-Email and X-Groups from oauth2-proxy 
# (requires running oauth2-proxy with --set-xauthrequest flag)
auth_request_set $user $upstream_http_x_auth_request_preferred_username;  
auth_request_set $email $upstream_http_x_auth_request_email;  
auth_request_set $groups $upstream_http_x_auth_request_groups;  
proxy_set_header X-User $user;
proxy_set_header X-Email $email;
proxy_set_header X-Groups $groups;
