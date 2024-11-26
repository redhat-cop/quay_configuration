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
module: quay_repository_prune
short_description: Manage auto-pruning policies for repositories
description:
  - Create or delete auto-pruning policies for repositories in Quay Container
    Registry.
version_added: '2.4.0'
author: Hervé Quatremain (@herve4m)
options:
  repository:
    description:
      - Name of the existing repository to configure. The format for the name is
        C(namespace)/C(shortname). The namespace can be an organization or your
        personal namespace.
      - If you omit the namespace part in the name, then the module looks for
        the repository in your personal namespace.
      - You can manage auto-pruning policies for repositories in your personal
        namespace, but not in the personal namespace of other users. The token
        you use in O(quay_token) determines the user account you are using.
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
    Repositories" permission.
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
- name: Ensure the repository keeps only five unstable images
  infra.quay_configuration.quay_repository_prune:
    repository: production/smallimage
    method: tags
    value: 5
    # Auto-pruning tags that contain "unstable" in their names
    tag_pattern: "unstable"
    tag_pattern_matches: true
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure the repository also prunes all tags older that seven weeks
  infra.quay_configuration.quay_repository_prune:
    repository: production/smallimage
    method: date
    value: 7w
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure the repository has only the defined auto-pruning policy
  infra.quay_configuration.quay_repository_prune:
    repository: development/frontend
    method: date
    value: 8d
    tag_pattern: "nightly"
    append: false
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure the auto-pruning policy is removed
  infra.quay_configuration.quay_repository_prune:
    repository: development/frontend
    method: date
    value: 8d
    tag_pattern: "nightly"
    state: absent
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure an auto-pruning policy exists for lvasquez's test repository
  infra.quay_configuration.quay_repository_prune:
    repository: lvasquez/test
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
        repository=dict(required=True),
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
    repository = module.params.get("repository")
    append = module.params.get("append")
    method = module.params.get("method")
    value = module.params.get("value")
    tag_pattern = module.params.get("tag_pattern")
    tag_pattern_matches = module.params.get("tag_pattern_matches")
    state = module.params.get("state")

    # Convert the parameters to a dictionary that can be used with the API
    data = module.process_prune_parameters(method, value, tag_pattern, tag_pattern_matches)

    namespace, repo_shortname, _not_used = module.split_name("repository", repository, state)
    full_repo_name = "{namespace}/{repository}".format(
        namespace=namespace, repository=repo_shortname
    )

    # Get the auto-pruning policies for the repository
    #
    # GET /api/v1/repository/{namespace}/{repository}/autoprunepolicy/
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
        "repository/{full_repo_name}/autoprunepolicy/", full_repo_name=full_repo_name
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
            "repository/{full_repo_name}/autoprunepolicy/{uuid}",
            full_repo_name=full_repo_name,
            uuid=policy_details.get("uuid", "") if policy_details else "",
        )

    if append and policy_details:
        module.exit_json(changed=False, id=policy_details.get("uuid"))

    if not policies:
        module.fail_json(
            msg="The {repo} repository does not exist.".format(repo=full_repo_name)
        )

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
                    "repository/{full_repo_name}/autoprunepolicy/{uuid}",
                    auto_exit=False,
                    full_repo_name=full_repo_name,
                    uuid=policy.get("uuid"),
                )
                deletions = True
        if policy_details:
            module.exit_json(changed=deletions, id=policy_details.get("uuid"))

    resp = module.create(
        "auto-pruning policy",
        method,
        "repository/{full_repo_name}/autoprunepolicy/",
        data,
        auto_exit=False,
        full_repo_name=full_repo_name,
    )
    module.exit_json(changed=True, id=resp.get("uuid"))


if __name__ == "__main__":
    main()
