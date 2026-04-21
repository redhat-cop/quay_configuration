#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026 Hervé Quatremain <herve.quatremain@redhat.com>
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
module: quay_capabilities_info
short_description: Return Quay's capabilities
description:
  - Return information about supported Quay features.
version_added: '2.8.0'
author: Hervé Quatremain (@herve4m)
notes:
  - The module requires Quay version 3.17 or later.
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
"""

EXAMPLES = r"""
- name: Retrieve Quay's capabilities
  infra.quay_configuration.quay_capabilities_info:
    quay_host: https://quay.example.com
  register: quay_capabilities
"""

RETURN = r"""
capabilities:
  description: Supported Quay features.
  returned: always
  type: dict
  sample: {
    "sparse_manifests": {
      "supported": true,
      "required_architectures": [],
      "optional_architectures_allowed": true
    },
    "mirror_architectures": [
      "amd64",
      "arm64",
      "ppc64le",
      "s390x"
    ]
  }
"""

from ..module_utils.api_module import APIModuleNoAuth


def main():
    # Create a module for ourselves
    module = APIModuleNoAuth(argument_spec={}, supports_check_mode=True)

    # Get Quay's capabilities
    #
    # GET /api/v1/registry/capabilities
    # {
    #   "sparse_manifests": {
    #     "supported": true,
    #     "required_architectures": [],
    #     "optional_architectures_allowed": true
    #   },
    #   "mirror_architectures": [
    #     "amd64",
    #     "arm64",
    #     "ppc64le",
    #     "s390x"
    #   ]
    # }
    c = module.get_object_path("registry/capabilities", duplicate_underscore=False)
    module.exit_json(changed=False, capabilities=c)


if __name__ == "__main__":
    main()
