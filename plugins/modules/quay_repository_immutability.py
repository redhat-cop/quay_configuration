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
module: quay_repository_immutability
short_description: Manage tag immutability policies for repositories
description:
  - Create, delete, and update tag immutability policies for a repository.
version_added: '2.8.0'
author: Hervé Quatremain (@herve4m)
options:
  repository:
    description:
      - Name of the existing repository to configure. The format for the name is
        C(namespace)/C(shortname). The namespace can be an organization or your
        personal namespace.
      - If you omit the namespace part in the name, then the module looks for
        the repository in your personal namespace.
      - You can manage tag immutability policies for repositories in your
        personal namespace, but not in the personal namespace of other users.
        The token you use in O(quay_token) determines the user account you are
        using.
    required: true
    type: str
  tag_pattern:
    description:
      - Regular expression to select the tags to protect.
    required: true
    type: str
  new_tag_pattern:
    description:
      - New regular expression for the immutability policy.
      - Setting this option changes the regular expression of the policy which
        current pattern is provided in O(tag_pattern).
    type: str
  behavior:
    description:
      - Specify the behavior of the matching pattern.
      - If V(matching_immutable), then tags that match the pattern are
        immutable.
      - If V(not_matching_immutable), then all the tags not matching the pattern
        are immutable.
      - V(matching_immutable) by default.
    type: str
    choices:
      - matching_immutable
      - not_matching_immutable
  state:
    description:
      - If V(absent), then the module deletes the immutability policy.
      - The module does not fail if the policy does not exist, because the
        state is already as expected.
      - If V(present), then the module creates the immutability policy if it
        does not already exist.
      - If the policy already exists, then the module updates its state.
    type: str
    default: present
    choices: [absent, present]
notes:
  - The module requires Quay version 3.17 or later.
  - To use the module, you must enable the tag immutability feature of your
    Quay installation (C(FEATURE_IMMUTABLE_TAGS) in C(config.yaml)).
  - The token that you provide in O(quay_token) must have the "Administer
    Repositories" permission.
  - See the M(infra.quay_configuration.quay_organization_immutability) module
    to manage tag immutability policies at the organization level.
  - See the M(infra.quay_configuration.quay_tag) module to manage the
    immutability of a specific tag.
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
- name: Ensure the immutability policy exists for tags that start with release
  infra.quay_configuration.quay_repository_immutability:
    repository: production/smallimage
    tag_pattern: "release.*"
    behavior: matching_immutable
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure the immutability policy is updated with a new pattern
  infra.quay_configuration.quay_repository_immutability:
    repository: production/smallimage
    tag_pattern: "release.*"
    new_tag_pattern: "prod-.*"
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure the immutability policy is removed
  infra.quay_configuration.quay_repository_immutability:
    repository: production/smallimage
    tag_pattern: "prod-.*"
    state: absent
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7
"""

RETURN = r""" # """

from ..module_utils.api_module import APIModule


def main():
    argument_spec = dict(
        repository=dict(required=True),
        tag_pattern=dict(required=True),
        new_tag_pattern=dict(),
        behavior=dict(choices=["matching_immutable", "not_matching_immutable"]),
        state=dict(choices=["present", "absent"], default="present"),
    )

    # Create a module for ourselves
    module = APIModule(argument_spec=argument_spec, supports_check_mode=True)

    # Extract our parameters
    repository = module.params.get("repository")
    tag_pattern = module.params.get("tag_pattern")
    new_tag_pattern = module.params.get("new_tag_pattern")
    behavior = module.params.get("behavior")
    state = module.params.get("state")

    namespace, repo_shortname, _not_used = module.split_name("repository", repository, state)
    full_repo_name = "{namespace}/{repository}".format(
        namespace=namespace, repository=repo_shortname
    )

    # Getting the immutability policies for the given repository
    #
    # GET /api/v1/repository/{namespace}/{repository}/immutabilitypolicy/
    # {
    #   "policies": [
    #     {
    #       "uuid": "3ab3aa03-2742-4947-9ed9-5429ad603dd4",
    #       "tagPattern": ".*",
    #       "tagPatternMatches": true
    #     }
    #   ]
    # }
    policy_list = module.get_object_path(
        "repository/{full_repo_name}/immutabilitypolicy/", full_repo_name=full_repo_name
    )

    # Looking for the policies
    policy_details = None
    new_policy_details = None
    if policy_list:
        for policy in policy_list.get("policies", []):
            policy_pattern = policy.get("tagPattern", "")
            if tag_pattern == policy_pattern:
                policy_details = policy
            elif new_tag_pattern == policy_pattern:
                new_policy_details = policy

    # The destination tag pattern already exists
    if policy_details and new_policy_details:
        module.fail_json(
            msg="The {pattern} tag pattern (`new_tag_pattern') already exists.".format(
                pattern=new_tag_pattern
            )
        )

    # Remove the policy
    if state == "absent":
        if new_policy_details:
            module.delete(
                new_policy_details,
                "immutability policy",
                new_tag_pattern,
                "repository/{full_repo_name}/immutabilitypolicy/{id}",
                full_repo_name=full_repo_name,
                id=new_policy_details.get("uuid", ""),
            )
        elif policy_details:
            module.delete(
                policy_details,
                "immutability policy",
                tag_pattern,
                "repository/{full_repo_name}/immutabilitypolicy/{id}",
                full_repo_name=full_repo_name,
                id=policy_details.get("uuid", ""),
            )
        else:
            module.exit_json(changed=False)

    if not policy_list:
        module.fail_json(
            msg="The {repo} repository does not exist.".format(repo=full_repo_name)
        )

    # Prepare the data that gets set for update or create
    new_fields = {}

    # Changing the tag pattern of an existing policy
    if new_tag_pattern:
        new_fields["tagPattern"] = new_tag_pattern
        # The original policy does not exists...
        if not policy_details:
            # and neither the policy for the new tag pattern.
            # Create that policy.
            if not new_policy_details:
                new_fields["tagPatternMatches"] = (
                    False if behavior == "not_matching_immutable" else True
                )
                module.create(
                    "immutability policy",
                    new_tag_pattern,
                    "repository/{full_repo_name}/immutabilitypolicy/",
                    new_fields,
                    full_repo_name=full_repo_name,
                )

            # The original policy does not exists but the new one does.
            # Update that new policy.
            if behavior is not None:
                new_fields["tagPatternMatches"] = (
                    True if behavior == "matching_immutable" else False
                )
            else:
                new_fields["tagPatternMatches"] = new_policy_details.get(
                    "tagPatternMatches", True
                )
            module.update(
                new_policy_details,
                "immutability policy",
                new_tag_pattern,
                "repository/{full_repo_name}/immutabilitypolicy/{id}",
                new_fields,
                full_repo_name=full_repo_name,
                id=new_policy_details.get("uuid", ""),
            )
    else:
        new_fields["tagPattern"] = tag_pattern

    if policy_details:
        if behavior is not None:
            new_fields["tagPatternMatches"] = (
                True if behavior == "matching_immutable" else False
            )
        else:
            new_fields["tagPatternMatches"] = policy_details.get("tagPatternMatches", True)
        module.update(
            policy_details,
            "immutability policy",
            tag_pattern,
            "repository/{full_repo_name}/immutabilitypolicy/{id}",
            new_fields,
            full_repo_name=full_repo_name,
            id=policy_details.get("uuid", ""),
        )

    new_fields["tagPatternMatches"] = False if behavior == "not_matching_immutable" else True
    module.create(
        "immutability policy",
        tag_pattern,
        "repository/{full_repo_name}/immutabilitypolicy/",
        new_fields,
        full_repo_name=full_repo_name,
    )


if __name__ == "__main__":
    main()
