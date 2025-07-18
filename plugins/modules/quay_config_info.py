#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025 Hervé Quatremain <herve.quatremain@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# For accessing the API documentation from a running system, use the swagger-ui
# container image:
#
#  $ podman run -p 8888:8080 --name=swag -d --rm \
#      -e API_URL=http://your.quay.installation:8080/api/v1/discovery \
#      docker.io/swaggerapi/swagger-ui
#
#  (replace the hostname and port in API_URL with your own installation)
#
# And then navigate to http://localhost:8888


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: quay_config_info
short_description: Return Quay's configuration
description:
  - Return current Quay's configuration.
version_added: '2.6.0'
author: Hervé Quatremain (@herve4m)
notes:
  - The module requires Quay version 3.15 or later.
  - The module requires that your Quay administrator enables dumping the
    configuration (C(FEATURE_SUPERUSER_CONFIGDUMP) to C(true) in
    C(config.yaml)).
  - The token that you provide in O(quay_token) must have the "Super User
    Access" permissions.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
  platform:
    support: full
    platforms: all
extends_documentation_fragment:
  - ansible.builtin.action_common_attributes
  - infra.quay_configuration.auth
  - infra.quay_configuration.auth.login
"""

EXAMPLES = r"""
- name: Retrieve Quay's configuration
  infra.quay_configuration.quay_config_info:
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7
  register: quay_conf
"""

RETURN = r"""
config:
  description: Configuration parameters.
  returned: always
  type: dict
  sample: {
    "SESSION_COOKIE_SECURE": false,
    "PREFERRED_URL_SCHEME": "http",
    "ACTION_LOG_ARCHIVE_LOCATION": "local_us",
    "ACTION_LOG_ARCHIVE_PATH": "actionlogarchive/",
    "ACTION_LOG_AUDIT_DELETE_FAILURES": false,
    "ACTION_LOG_AUDIT_LOGINS": true,
    "ACTION_LOG_AUDIT_LOGIN_FAILURES": false,
    "ACTION_LOG_AUDIT_PULL_FAILURES": false,
    "ACTION_LOG_AUDIT_PUSH_FAILURES": false,
    "ACTION_LOG_ROTATION_THRESHOLD": "30d",
    "ALLOWED_OCI_ARTIFACT_TYPES": {
      "application/vnd.oci.image.config.v1+json": [
        "application/vnd.dev.cosign.simplesigning.v1+json",
        "application/vnd.dsse.envelope.v1+json",
        "text/spdx",
        "text/spdx+xml",
        "text/spdx+json",
        "application/vnd.syft+json",
        "application/vnd.cyclonedx",
        "application/vnd.cyclonedx+xml",
        "application/vnd.cyclonedx+json",
        "application/vnd.in-toto+json"
      ],
      "application/vnd.cncf.helm.config.v1+json": [
        "application/tar+gzip",
        "application/vnd.cncf.helm.chart.content.v1.tar+gzip"
      ],
      "application/vnd.oci.source.image.config.v1+json": [
        "application/vnd.oci.image.layer.v1.tar+gzip"
      ],
      "application/vnd.unknown.config.v1+json": [
        "application/vnd.cncf.openpolicyagent.policy.layer.v1+rego",
        "application/vnd.cncf.openpolicyagent.data.layer.v1+json"
      ]
    },
    "ALLOW_PULLS_WITHOUT_STRICT_LOGGING": true,
    "ALLOW_WITHOUT_STRICT_LOGGING": false,
    "AUTHENTICATION_TYPE": "Database",
    "AVATAR_KIND": "local",
  }
"""

from ..module_utils.api_module import APIModule


def main():
    # Create a module for ourselves
    module = APIModule(argument_spec={}, supports_check_mode=True)

    # Get Quay's configuration
    #
    # GET /api/v1/superuser/config
    # {
    #   "config": {
    #     "SESSION_COOKIE_SECURE": false,
    #     "PREFERRED_URL_SCHEME": "http",
    #     "ACTION_LOG_ARCHIVE_LOCATION": "local_us",
    #     "ACTION_LOG_ARCHIVE_PATH": "actionlogarchive/",
    #     "ACTION_LOG_AUDIT_DELETE_FAILURES": false,
    #     "ACTION_LOG_AUDIT_LOGINS": true,
    #     "ACTION_LOG_AUDIT_LOGIN_FAILURES": false,
    #     "ACTION_LOG_AUDIT_PULL_FAILURES": false,
    #     "ACTION_LOG_AUDIT_PUSH_FAILURES": false,
    #     "ACTION_LOG_ROTATION_THRESHOLD": "30d",
    #     "ALLOWED_OCI_ARTIFACT_TYPES": {
    #       "application/vnd.oci.image.config.v1+json": [
    #         "application/vnd.dev.cosign.simplesigning.v1+json",
    #         "application/vnd.dsse.envelope.v1+json",
    #         "text/spdx",
    #         "text/spdx+xml",
    #         "text/spdx+json",
    #         "application/vnd.syft+json",
    #         "application/vnd.cyclonedx",
    #         "application/vnd.cyclonedx+xml",
    #         "application/vnd.cyclonedx+json",
    #         "application/vnd.in-toto+json"
    #       ],
    #       "application/vnd.cncf.helm.config.v1+json": [
    #         "application/tar+gzip",
    #         "application/vnd.cncf.helm.chart.content.v1.tar+gzip"
    #       ],
    #       "application/vnd.oci.source.image.config.v1+json": [
    #         "application/vnd.oci.image.layer.v1.tar+gzip"
    #       ],
    #       "application/vnd.unknown.config.v1+json": [
    #         "application/vnd.cncf.openpolicyagent.policy.layer.v1+rego",
    #         "application/vnd.cncf.openpolicyagent.data.layer.v1+json"
    #       ]
    #     },
    #     ...
    #   }
    # }
    c = module.get_object_path("superuser/config")
    module.exit_json(changed=False, config=c.get("config", {}))


if __name__ == "__main__":
    main()
