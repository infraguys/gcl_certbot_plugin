#    Copyright 2025 Genesis Corporation.
#
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from gcl_iam.tests.functional import clients as iam_clients


from certbot import errors
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Authenticator(dns_common.DNSAuthenticator):

    description = "Obtain certificates with Genesis Core DNS server"

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)

        self._zone_uuid = None
        self._record_uuid = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds=0
        )
        add(
            "endpoint",
            help="Core API endpoint.",
            default="http://core.local.genesis-core.tech:11010/v1",
        )
        add("login", help="Core API login.")
        add("password", help="Core API password.")

    def _setup_credentials(self):
        if not all((self.conf("login"), self.conf("password"))):
            raise errors.MisconfigurationError(
                "Credentials are not configured, please set --genesis-core-login and --genesis-core-password"
            )
        auth = iam_clients.GenesisCoreAuth(
            username=self.conf("login"), password=self.conf("password")
        )

        self.client = iam_clients.GenesisCoreTestRESTClient(
            endpoint=self.conf("endpoint"), auth=auth
        )

        # Check credentials here to minimize other requests.
        url = self.client.build_collection_uri(["dns", "domains"])
        self.client.get(url)

    def more_info(self):
        return "This plugin uses integrated Genesis Core DNS server to perform DNS-01 checks."

    def _perform(self, domain, validation_name, validation):
        url = self.client.build_collection_uri(["dns", "domains"])
        zone = None
        parent_domain = domain
        # Try to find target zone iteratively.
        while parent_domain:
            try:
                parent_domain = parent_domain.split(".", 1)[1]
            except IndexError:
                break

            response = self.client.get(
                url, params={"name": parent_domain}
            ).json()
            if response:
                zone = response[0]
                break
        if not zone:
            raise errors.PluginError(
                "Could not find DNS zone for domain %s" % domain
            )

        self._zone_uuid = zone["uuid"]

        data = {
            "type": "TXT",
            "ttl": 0,
            "record": {
                "kind": "TXT",
                "name": validation_name.removesuffix(f".{zone['name']}"),
                "content": validation,
            },
        }

        url = self.client.build_collection_uri(
            ["dns", "domains", self._zone_uuid, "records"]
        )

        record = self.client.post(url, json=data).json()

        self._record_uuid = record["uuid"]

    def _cleanup(self, domain, validation_name, validation):
        if not self._zone_uuid or not self._record_uuid:
            return

        url = self.client.build_resource_uri(
            ["dns", "domains", self._zone_uuid, "records", self._record_uuid]
        )

        self.client.delete(url)
