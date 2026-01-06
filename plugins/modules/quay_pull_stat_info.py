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
module: quay_pull_stat_info
short_description: Return image pull statistics for tags and manifests
description:
  - Return image pull statistics for tags and manifests.
version_added: '2.7.0'
author: Hervé Quatremain (@herve4m)
options:
  repository:
    description:
      - Name of the repository that contains the image. The format is
        C(namespace)/C(shortname). The namespace can be an organization or a
        personal namespace.
      - If you omit the namespace part, then the module looks for the
        repository in your personal namespace.
    required: true
    type: str
  tag:
    description:
      - Return image pull statistics from the image's tag.
      - If you omit O(tag) and O(digest), then the C(latest) tag is assumed.
      - Mutually exclusive with O(digest).
    type: str
  digest:
    description:
      - Return image pull statistics from the image's digest.
      - If you omit O(tag) and O(digest), then the C(latest) tag is assumed.
      - Mutually exclusive with O(tag).
    type: str
notes:
  - The module requires Quay version 3.16 or later.
  - The module requires that your Quay administrator enables image statistics
    for your installation (by setting C(FEATURE_IMAGE_PULL_STATS) to C(True) in
    C(config.yaml)).
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
- name: Retrieve the pull statistics for the production/smallimage:0.1.2 image
  infra.quay_configuration.quay_pull_stat_info:
    repository: production/smallimage
    tag: "0.1.2"
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7
  register: stats

- name: Retrieve the pull statistics for the images with the given digest
  infra.quay_configuration.quay_pull_stat_info:
    repository: production/smallimage
    digest: "sha256:53b2...a7c8"
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7
  register: stats
"""

RETURN = r"""
tag_name:
  description: Name of the tag.
  type: str
  returned: Only when getting statistics by tags.
  sample: 0.1.2
tag_pull_count:
  description: Number of times that the image was pulled by its tag.
  type: int
  returned: Only when getting statistics by tags.
  sample: 42
last_tag_pull_date:
  description: Date and time of the last pull operation.
  type: str
  returned: Only when getting statistics by tags.
  sample: Mon, 29 Dec 2025 15:53:23 -0000
manifest_digest:
  description: SHA256 digest of the image.
  type: str
  returned: always
  sample: sha256:a8f231c07da40107543d74ed1e9a1938a004b498377dbefcf29082c7a9e55ea7
manifest_pull_count:
  description: Number of times that the image was pulled by its digest.
  type: int
  returned: always.
  sample: 42
last_manifest_pull_date:
  description: Date and time of the last pull operation.
  type: str
  returned: always.
  sample: Mon, 29 Dec 2025 15:53:23 -0000
"""

from ..module_utils.api_module import APIModule
from ..module_utils.quay_image import QuayImage


def exit_module(module, data):
    """Exit the module and return data.

    :param module: The module object.
    :type module: :py:class:``APIModule``
    :param data: The data returned by the API call.
    :type data: dict
    """
    result = {"changed": False}
    if data:
        result.update(data)
        # Rename the "current_manifest_digest" key to "manifest_digest"
        if "current_manifest_digest" in result:
            result["manifest_digest"] = result["current_manifest_digest"]
            del result["current_manifest_digest"]
        # Delete the fields that were duplicated by the get_object_path method
        result.pop("currentmanifestdigest", None)
        result.pop("lastmanifestpulldate", None)
        result.pop("lasttagpulldate", None)
        result.pop("manifestpullcount", None)
        result.pop("tagname", None)
        result.pop("tagpullcount", None)
    module.exit_json(**result)


def main():
    argument_spec = dict(
        repository=dict(required=True),
        tag=dict(),
        digest=dict(),
    )

    mutually_exclusive = [("tag", "digest")]

    # Create a module for ourselves
    module = APIModule(
        argument_spec=argument_spec,
        mutually_exclusive=mutually_exclusive,
        supports_check_mode=True,
    )

    # Extract our parameters
    name = module.params.get("repository").strip("/")
    tag = module.params.get("tag")
    digest = module.params.get("digest")

    # Get the components of the given image (namespace, repository)
    img = QuayImage(module, name)
    namespace = img.namespace
    if namespace is None:
        module.fail_json(
            msg=(
                "The `repository' parameter must include the"
                " organization: <organization>/{name}."
            ).format(name=name)
        )

    # Check whether the namespace exists (organization or user account)
    namespace_details = module.get_namespace(namespace)
    if not namespace_details:
        module.exit_json(changed=False, stats=[])

    if digest:
        # Get the stat from the digest
        #
        # GET /api/v1/repository/{ns}/{repo}/manifest/{digest}/pull_statistics
        # {
        #   "manifest_digest": "sha256:1751...2895",
        #   "manifest_pull_count": 0,
        #   "last_manifest_pull_date": null
        # }
        stats = module.get_object_path(
            "repository/{namespace}/{repository}/manifest/{digest}/pull_statistics",
            namespace=namespace,
            repository=img.repository,
            digest=digest,
        )
        exit_module(module, stats)

    else:
        # Get the stat from the tag
        #
        # GET /api/v1/repository/{ns}/{repo}/tag/{tag}/pull_statistics
        # {
        #   "tag_name": "0.1.2",
        #   "tag_pull_count": 0,
        #   "last_tag_pull_date": null,
        #   "current_manifest_digest": "sha256:1751...2895",
        #   "manifest_pull_count": 0,
        #   "last_manifest_pull_date": null
        # }
        stats = module.get_object_path(
            "repository/{namespace}/{repository}/tag/{tag}/pull_statistics",
            namespace=namespace,
            repository=img.repository,
            tag=tag if tag else "latest",
        )
        exit_module(module, stats)


if __name__ == "__main__":
    main()
