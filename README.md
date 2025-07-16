# gcl_certbot_plugin
Plugin for certbot to allow dns-01 acme checks in letsencrypt with Genesis Core integrated DNS.

## How to use
```bash
# Install the plugin and certbot
pip install gcl_certbot_plugin

# Create certificate
certbot certonly --authenticator=genesis-core \
    --genesis-core-endpoint=http://core.local.genesis-core.tech:11010 \
    --genesis-core-login=admin \
    --genesis-core-password=password \
    --domains test.pdns.your.domain
```

To create a new certificate, in the code
```python
from gcl_certbot_plugin import acme

# Get or creat a client private key
private_key = acme.get_or_create_client_private_key("privkey.pem")

# Get ACME client
client_acme = acme.get_acme_client(private_key, "myemail@example.com")

# Create cert
pkey_pem, csr_pem, fullchain_pem = acme.create_cert(
    client_acme,
    dns_client,
    ["test.pdns.your.domain"],
)
```

For complete example see [create_cert](https://github.com/infraguys/gcl_certbot_plugin/blob/master/gcl_certbot_plugin/examples/create_cert.py) script.
