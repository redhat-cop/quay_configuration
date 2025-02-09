#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024 Hervé Quatremain <herve.quatremain@redhat.com>
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
module: quay_organization_prune
short_description: Manage auto-pruning policies for organizations and user namespaces
description:
  - Create or delete auto-pruning policies for organizations and personal
    namespaces in Quay Container Registry.
version_added: '2.4.0'
author: Hervé Quatremain (@herve4m)
options:
  namespace:
    description:
      - Organization or personal namespace. This namespace must exist.
    required: true
    type: str
  append:
    description:
      - If V(true), then add the auto-pruning policy to the existing policies.
      - If V(false), then the module deletes all the existing auto-pruning
        policies before adding the specified policy.
    type: bool
    default: true
  state:
    description:
      - If V(absent), then the module deletes the auto-pruning policy that
        matches the provided parameters.
      - The module does not fail if the policy does not exist, because the
        state is already as expected.
      - If V(present), then the module creates the auto-pruning policy if it
        does not already exist.
    type: str
    default: present
    choices: [absent, present]
notes:
  - The token that you provide in O(quay_token) must have the "Administer
    Organization" permission.
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
  - infra.quay_configuration.autoprune
"""

EXAMPLES = r"""
- name: Ensure the organization keeps only five unstable images
  infra.quay_configuration.quay_organization_prune:
    namespace: production
    method: tags
    value: 5
    # Auto-pruning tags that contain "unstable" in their names
    tag_pattern: "unstable"
    tag_pattern_matches: true
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure the organization also prunes all tags older that seven weeks
  infra.quay_configuration.quay_organization_prune:
    namespace: production
    method: date
    value: 7w
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure the organization has only the defined auto-pruning policy
  infra.quay_configuration.quay_organization_prune:
    namespace: development
    method: date
    value: 8d
    tag_pattern: "nightly"
    append: false
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure the auto-pruning policy is removed
  infra.quay_configuration.quay_organization_prune:
    namespace: development
    method: date
    value: 8d
    tag_pattern: "nightly"
    state: absent
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure an auto-pruning policy exists in lvasquez's personal namespace
  infra.quay_configuration.quay_organization_prune:
    namespace: lvasquez
    method: date
    value: 8d
    tag_pattern: "nightly"
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7
"""

RETURN = r"""
id:
  description: Internal identifier of the auto-pruning policy.
  type: str
  returned: always
  sample: 45b4cc8b-178b-4ad4-bd33-75e3cce5e889
"""

from ..module_utils.api_module import APIModule


def main():
    argument_spec = dict(
        namespace=dict(required=True),
        append=dict(type="bool", default=True),
        method=dict(choices=["tags", "date"], required=True),
        value=dict(required=True),
        tag_pattern=dict(),
        tag_pattern_matches=dict(type="bool", default=True),
        state=dict(choices=["present", "absent"], default="present"),
    )

    # Create a module for ourselves
    module = APIModule(argument_spec=argument_spec, supports_check_mode=True)

    # Extract our parameters
    namespace = module.params.get("namespace")
    append = module.params.get("append")
    method = module.params.get("method")
    value = module.params.get("value")
    tag_pattern = module.params.get("tag_pattern")
    tag_pattern_matches = module.params.get("tag_pattern_matches")
    state = module.params.get("state")

    # Convert the parameters to a dictionary that can be used with the API
    data = module.process_prune_parameters(method, value, tag_pattern, tag_pattern_matches)

    # Check whether namespace exists (organization or user account)
    if not module.get_namespace(namespace):
        if state == "absent":
            module.exit_json(changed=False)
        module.fail_json(
            msg="The {orgname} organization or personal namespace does not exist.".format(
                orgname=namespace
            )
        )

    # Get the auto-pruning policies for the organization
    #
    # GET /api/v1/organization/{orgname}/autoprunepolicy/
    #
    # {
    #   "policies": [
    #     {
    #       "uuid": "dc84065e-9e9c-43e9-9224-6151c80219b9",
    #       "method": "creation_date",
    #       "value": "10w",
    #       "tagPattern": "dev.*",
    #       "tagPatternMatches": true
    #     },
    #     {
    #       "uuid": "b0515264-91da-46c1-829d-11230a9721a8",
    #       "method": "number_of_tags",
    #       "value": 20,
    #       "tagPattern": "prod.*",
    #       "tagPatternMatches": false
    #     },
    #     {
    #       "uuid": "71fd827c-6dec-4ecd-ac92-a200e821afa9",
    #       "method": "number_of_tags",
    #       "value": 25,
    #       "tagPattern": null,
    #       "tagPatternMatches": true
    #     }
    #   ]
    # }
    policies = module.get_object_path(
        "organization/{orgname}/autoprunepolicy/", orgname=namespace
    )

    # Finding a matching auto-pruning policy
    policy_details = None
    if policies:
        for policy in policies.get("policies", []):
            if (
                policy.get("method") == data.get("method")
                and policy.get("value") == data.get("value")
                and policy.get("tagPattern") == data.get("tagPattern")
                and policy.get("tagPatternMatches") == data.get("tagPatternMatches", True)
            ):
                policy_details = policy
                break

    # Remove the auto-pruning policy
    if state == "absent":
        module.delete(
            policy_details,
            "auto-pruning policy",
            method,
            "organization/{orgname}/autoprunepolicy/{uuid}",
            orgname=namespace,
            uuid=policy_details.get("uuid", "") if policy_details else "",
        )

    if append and policy_details:
        module.exit_json(changed=False, id=policy_details.get("uuid"))

    # Remove all the auto-pruning policies, except the one that the user
    # specifies
    if not append:
        deletions = False
        for policy in policies.get("policies", []):
            if not policy_details or (policy_details.get("uuid") != policy.get("uuid")):
                module.delete(
                    policy,
                    "auto-pruning policy",
                    policy.get("method"),
                    "organization/{orgname}/autoprunepolicy/{uuid}",
                    auto_exit=False,
                    orgname=namespace,
                    uuid=policy.get("uuid"),
                )
                deletions = True
        if policy_details:
            module.exit_json(changed=deletions, id=policy_details.get("uuid"))

    resp = module.create(
        "auto-pruning policy",
        method,
        "organization/{orgname}/autoprunepolicy/",
        data,
        auto_exit=False,
        orgname=namespace,
    )
    module.exit_json(changed=True, id=resp.get("uuid"))


if __name__ == "__main__":
    main()
