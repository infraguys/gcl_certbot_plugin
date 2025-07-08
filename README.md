# gcl_certbot_plugin
Plugin for certbot to allow dns-01 acme checks in letsencrypt with Genesis Core integrated DNS.

## How to use
```bash
# Install the plugin and certbot
pip install gcl_certbot_plugin

# Create certificate
certbot certonly --authenticator=genesis-core \
    --genesis-core-endpoint=http://local.genesis-core.tech:11010/v1 \
    --genesis-core-login=admin \
    --genesis-core-password=password \
    --domains test.pdns.your.domain
```

