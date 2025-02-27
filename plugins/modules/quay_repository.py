#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021-2024 Hervé Quatremain <herve.quatremain@redhat.com>
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
module: quay_repository
short_description: Manage Quay Container Registry repositories
description:
  - Create, delete, and update repositories in Quay Container Registry.
version_added: '0.0.1'
author: Hervé Quatremain (@herve4m)
options:
  name:
    description:
      - Name of the repository to create, remove, or modify. The format for the
        name is C(namespace)/C(shortname). The namespace can be an organization
        or your personal namespace.
      - The name must be in lowercase and must not contain white spaces.
      - If you omit the namespace part in the name, then the module uses your
        personal namespace.
      - You can manage repositories in your personal namespace,
        but not in the personal namespace of other users. The token you use in
        O(quay_token) determines the user account you are using.
    required: true
    type: str
  visibility:
    description:
      - If V(public), then anyone can pull images from the repository.
      - If V(private), then nobody can access the repository and you need to
        explicitly grant access to users, robots, and teams.
      - If you do not set the parameter when you create a repository, then
        it defaults to V(private).
    type: str
    choices: [public, private]
  description:
    description:
      - Text in Markdown format that describes the repository.
    type: str
  perms:
    description:
      - User, robot, and team permissions to associate with the repository.
    type: list
    elements: dict
    suboptions:
      type:
        description:
          - Specifies the type of the account. Choose V(user) for both user and
            robot accounts.
        type: str
        choices: [user, team]
        default: user
      name:
        description:
          - Name of the account. The format for robot accounts is
            C(namespace)+C(shortrobotname).
        required: true
        type: str
      role:
        description:
          - Type of permission to grant.
        type: str
        choices: [read, write, admin]
        default: read
  append:
    description:
      - If V(true), then add the permission defined in O(perms) to the
        repository.
      - If V(false), then the module sets the permissions specified in O(perms),
        removing all others permissions from the repository.
    type: bool
    default: true
  star:
    description:
      - If V(true), then add a star to the repository. If V(false), then remove
        the star.
      - To star or unstar a repository you must provide the O(quay_token)
        parameter to authenticate. If you are not authenticated, then the
        module ignores the O(star) parameter.
    type: bool
  state:
    description:
      - If V(absent), then the module deletes the repository.
      - The module does not fail if the repository does not exist, because the
        state is already as expected.
      - If V(present), then the module creates the repository if it does not
        already exist.
      - If the repository already exists, then the module updates its state.
    type: str
    default: present
    choices: [absent, present]
  repo_state:
    description:
      - If V(NORMAL), then the repository is in the default state (read/write).
      - If V(READ_ONLY), then the repository is read-only.
      - If V(MIRROR), then the repository is a mirror and you can configure it
        by using the M(infra.quay_configuration.quay_repository_mirror) module.
      - You must enable the mirroring capability of your Quay installation to
        use this O(repo_state) parameter.
    type: str
    choices: [NORMAL, READ_ONLY, MIRROR]
notes:
  - Your Quay administrator must enable the mirroring capability of your Quay
    installation (C(FEATURE_REPO_MIRROR) in C(config.yaml)) to use the
    O(repo_state) parameter.
  - The token that you provide in O(quay_token) must have the "Administer
    Repositories" and "Create Repositories" permissions.
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
  - infra.quay_configuration.autoprune_deprecated
"""

EXAMPLES = r"""
- name: Ensure repository smallimage exists in the production organization
  infra.quay_configuration.quay_repository:
    name: production/smallimage
    visibility: private
    description: |
      # My first repository

      * smallimage is a small GNU/linux container image
      * Use podman to start a container using that image
    perms:
      - name: operators
        type: team
        role: read
      - name: lvasquez
        type: user
        role: read
      - name: production+automationrobot
        type: user
        role: admin
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure repository bigimage exists in my namespace
  infra.quay_configuration.quay_repository:
    name: bigimage
    visibility: public
    perms:
      - name: dwilde
        type: user
        role: write
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure repository development/testimg does not exist
  infra.quay_configuration.quay_repository:
    name: development/testimg
    state: absent
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure the repository has the exact set of permissions
  infra.quay_configuration.quay_repository:
    name: production/smallimage
    perms:
      - name: operators
        type: team
        role: admin
      - name: managers
        type: team
        role: read
      - name: developers
        type: team
        role: read
      - name: production+auditrobot
        type: user
        role: read
    append: false
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure the repository has a star
  infra.quay_configuration.quay_repository:
    name: production/smallimage
    star: true
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

# You must enable the mirroring capability of your Quay installation
# to use the repo_state parameter.
- name: Ensure the repository is prepared for mirroring
  infra.quay_configuration.quay_repository:
    name: production/smallimage
    repo_state: MIRROR
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7
"""

RETURN = r""" # """

import re

from ..module_utils.api_module import APIModule


def main():
    argument_spec = dict(
        name=dict(required=True),
        visibility=dict(choices=["public", "private"]),
        description=dict(),
        perms=dict(
            type="list",
            elements="dict",
            options=dict(
                type=dict(choices=["user", "team"], default="user"),
                name=dict(required=True),
                role=dict(choices=["read", "write", "admin"], default="read"),
            ),
        ),
        append=dict(type="bool", default=True),
        star=dict(type="bool"),
        repo_state=dict(choices=["NORMAL", "READ_ONLY", "MIRROR"]),
        auto_prune_method=dict(
            choices=["none", "tags", "date"],
            removed_at_date="2025-12-01",
            removed_from_collection="infra.quay_configuration",
        ),
        auto_prune_value=dict(
            removed_at_date="2025-12-01", removed_from_collection="infra.quay_configuration"
        ),
        state=dict(choices=["present", "absent"], default="present"),
    )

    # Create a module for ourselves
    module = APIModule(
        argument_spec=argument_spec,
        required_if=[
            ("auto_prune_method", "tags", ["auto_prune_value"]),
            ("auto_prune_method", "date", ["auto_prune_value"]),
        ],
        required_by={
            "auto_prune_value": "auto_prune_method",
        },
        supports_check_mode=True,
    )

    # Extract our parameters
    name = module.params.get("name").strip("/")
    visibility = module.params.get("visibility")
    description = module.params.get("description")
    perms = module.params.get("perms")
    append = module.params.get("append")
    star = module.params.get("star")
    repo_state = module.params.get("repo_state")
    auto_prune_method = module.params.get("auto_prune_method")
    auto_prune_value = module.params.get("auto_prune_value")
    state = module.params.get("state")

    # Validate the auto-pruning tags values
    if auto_prune_method == "tags":
        try:
            auto_prune_value = int(auto_prune_value)
        except ValueError:
            module.fail_json(
                msg=(
                    "Wrong format for the `auto_prune_value' parameter:"
                    " {auto_prune_value} is not a positive integer."
                ).format(auto_prune_value=auto_prune_value)
            )
        if auto_prune_value <= 0:
            module.fail_json(
                msg=(
                    "Wrong format for the `auto_prune_value' parameter:"
                    " {auto_prune_value} is not a positive integer."
                ).format(auto_prune_value=auto_prune_value)
            )
    if auto_prune_method == "date":
        value = "".join(auto_prune_value.split())
        if not re.match(r"[1-9]\d*[smhdw]$", value):
            module.fail_json(
                msg=(
                    "Wrong format for the `auto_prune_value' parameter:"
                    " {auto_prune_value} is not a positive integer followed by"
                    " the s, m, h, d, or w suffix."
                ).format(auto_prune_value=auto_prune_value)
            )
        auto_prune_value = value

    namespace, repo_shortname, _not_used = module.split_name("name", name, state)
    full_repo_name = "{namespace}/{repository}".format(
        namespace=namespace, repository=repo_shortname
    )

    # Get the repository details
    #
    # GET /api/v1/repository/{namespace}/{repository}
    # {
    #   "namespace": "production",
    #   "name": "busybox",
    #   "kind": "image",
    #   "description": "Busybox images",
    #   "is_public": true,
    #   "is_organization": true,
    #   "is_starred": false,
    #   "status_token": "",
    #   "trust_enabled": false,
    #   "tag_expiration_s": 86400,
    #   "is_free_account": true,
    #   "state": "NORMAL",
    #   "tags": {},
    #   "can_write": true,
    #   "can_admin": true
    # }
    repo_details = module.get_object_path(
        "repository/{full_repo_name}", full_repo_name=full_repo_name
    )

    # Remove the repository
    if state == "absent":
        module.delete(
            repo_details,
            "repository",
            full_repo_name,
            "repository/{full_repo_name}",
            full_repo_name=full_repo_name,
        )

    changed = False
    if not repo_details:
        # Create the repository
        new_fields = {
            "namespace": namespace,
            "repository": repo_shortname,
            "repo_kind": "image",
        }
        new_fields["description"] = description if description else ""
        new_fields["visibility"] = visibility if visibility else "private"
        module.create("repository", full_repo_name, "repository", new_fields, auto_exit=False)
        changed = True
    else:
        # Update description
        if description is not None:
            updated, _not_used = module.update(
                repo_details,
                "repository",
                full_repo_name,
                "repository/{full_repo_name}",
                {"description": description},
                auto_exit=False,
                full_repo_name=full_repo_name,
            )
            if updated:
                changed = True
        # Update visibility
        if (
            visibility
            and "is_public" in repo_details
            and (
                repo_details["is_public"]
                and visibility == "private"
                or not repo_details["is_public"]
                and visibility == "public"
            )
        ):
            module.create(
                "repository",
                full_repo_name,
                "repository/{full_repo_name}/changevisibility",
                {"visibility": visibility},
                auto_exit=False,
                full_repo_name=full_repo_name,
            )
            changed = True

    if repo_state is not None and (
        not repo_details
        and repo_state != "NORMAL"
        or repo_details
        and repo_details.get("state") != repo_state
    ):
        # Update repo_state
        module.unconditional_update(
            "repository",
            full_repo_name,
            "repository/{full_repo_name}/changestate",
            {"state": repo_state},
            full_repo_name=full_repo_name,
        )
        changed = True

    if star is not None and module.authenticated:
        if star and (not repo_details or not repo_details.get("is_starred")):
            module.create(
                "repository",
                full_repo_name,
                "user/starred",
                {"namespace": namespace, "repository": repo_shortname},
                auto_exit=False,
            )
            changed = True
        if not star and repo_details and repo_details.get("is_starred"):
            module.delete(
                repo_details,
                "repository",
                full_repo_name,
                "user/starred/{full_repo_name}",
                auto_exit=False,
                full_repo_name=full_repo_name,
            )
            changed = True

    #
    # Process the auto-pruning tags policy configuration
    #

    if auto_prune_method is not None:

        # Get the current auto-pruning tags policy:
        #
        # GET /api/v1/repository/{namespace}/{repository}/autoprunepolicy/
        # {
        #   "policies": [
        #     {
        #       "uuid": "e54f146d-eb0e-446c-9057-61291a0b257c",
        #       "method": "creation_date",
        #       "value": "7h"
        #     }
        #   ]
        # }
        #
        # If no policy is defined, then the returned data is {"policies": []}
        prune_details = module.get_object_path(
            "repository/{full_repo_name}/autoprunepolicy/",
            full_repo_name=full_repo_name,
        )
        try:
            policies = prune_details["policies"]
        except (TypeError, IndexError):
            policies = []

        # Removing all the auto-pruning policies
        if auto_prune_method == "none":
            deleted = False
            for policy in policies:
                uuid = policy.get("uuid")
                if module.delete(
                    uuid,
                    "repository auto-pruning policy",
                    full_repo_name,
                    "repository/{full_repo_name}/autoprunepolicy/{uuid}",
                    auto_exit=False,
                    full_repo_name=full_repo_name,
                    uuid=uuid,
                ):
                    deleted = True
            if deleted:
                changed = True
        else:
            # Compose the request
            method = "creation_date" if auto_prune_method == "date" else "number_of_tags"
            new_policy = {
                "method": method,
                "value": auto_prune_value,
            }

            # Verify whether the policy already exists
            for policy in policies:
                # The policy already exists
                if policy.get("method") == method and policy.get("value") == auto_prune_value:
                    break
            else:
                # The policy does not exist. If a policy is not already defined,
                # then create the policy
                if len(policies) == 0 or policies[0].get("uuid") is None:
                    module.create(
                        "repository auto-pruning policy",
                        full_repo_name,
                        "repository/{full_repo_name}/autoprunepolicy/",
                        new_policy,
                        auto_exit=False,
                        full_repo_name=full_repo_name,
                    )
                    changed = True
                else:
                    # Update the existing policy (the first one in the list)
                    uuid = policies[0]["uuid"]
                    new_policy["uuid"] = uuid
                    module.unconditional_update(
                        "repository auto-pruning policy",
                        full_repo_name,
                        "repository/{full_repo_name}/autoprunepolicy/{uuid}",
                        new_policy,
                        full_repo_name=full_repo_name,
                        uuid=uuid,
                    )
                    changed = True

    # No permission to change. Exit
    if perms is None:
        module.exit_json(changed=changed)

    # Get the team permissions
    #
    # GET /api/v1/repository/{namespace}/{repository}/permissions/team/
    # {
    #   "permissions": {
    #     "developers": {
    #       "role": "write",
    #       "name": "developers",
    #       "avatar": {
    #         "name": "developers",
    #         "hash": "5760...397e",
    #         "color": "#9c9ede",
    #         "kind": "team"
    #       }
    #     }
    #   }
    # }
    team_perms = module.get_object_path(
        "repository/{full_repo_name}/permissions/team/", full_repo_name=full_repo_name
    )

    # Set of (<team>, <perm>) tuples
    current_team_perms = set(
        [(p["name"], p["role"]) for _not_used, p in team_perms.get("permissions", {}).items()]
    )
    new_team_perms = set(
        [(p["name"], p["role"]) for p in perms if p.get("type", "user") == "team"]
    )

    to_add = new_team_perms - current_team_perms
    if append:
        to_delete = set()
    else:
        to_delete = current_team_perms - new_team_perms

    # Checking that all the teams to add exist
    teams_not_found = []
    for team in to_add:
        if module.get_team(namespace, team[0]) is None:
            teams_not_found.append(team[0])
    if teams_not_found:
        module.fail_json(
            msg=(
                "At least one team to associate to the repository does not exist: {teams}."
            ).format(teams=", ".join(teams_not_found))
        )

    for perm in to_delete:
        module.delete(
            True,
            "team repository permission",
            perm[0],
            "repository/{full_repo_name}/permissions/team/{team}",
            auto_exit=False,
            full_repo_name=full_repo_name,
            team=perm[0],
        )
        changed = True

    for perm in to_add:
        module.unconditional_update(
            "team repository permission",
            perm[0],
            "repository/{full_repo_name}/permissions/team/{team}",
            {"role": perm[1]},
            full_repo_name=full_repo_name,
            team=perm[0],
        )
        changed = True

    # Get the user permissions
    #
    # GET /api/v1/repository/{namespace}/{repository}/permissions/user/
    # {
    #   "permissions": {
    #     "admin": {
    #       "role": "admin",
    #       "name": "admin",
    #       "is_robot": false,
    #       "avatar": {
    #         "name": "admin",
    #         "hash": "258d...da4f",
    #         "color": "#98df8a",
    #         "kind": "user"
    #       },
    #       "is_org_member": true
    #     },
    #     "operator2": {
    #       "role": "write",
    #       "name": "operator2",
    #       "is_robot": false,
    #       "avatar": {
    #         "name": "operator2",
    #         "hash": "4eaf...94b0",
    #         "color": "#7f7f7f",
    #         "kind": "user"
    #       },
    #       "is_org_member": false
    #     }
    #   }
    # }
    user_perms = module.get_object_path(
        "repository/{full_repo_name}/permissions/user/", full_repo_name=full_repo_name
    )

    # Set of (<user>, <perm>) tuples
    current_user_perms = set(
        [(p["name"], p["role"]) for _not_used, p in user_perms.get("permissions", {}).items()]
    )
    new_user_perms = set(
        [(p["name"], p["role"]) for p in perms if p.get("type", "user") == "user"]
    )

    to_add = new_user_perms - current_user_perms
    if append:
        to_delete = set()
    else:
        to_delete = current_user_perms - new_user_perms

    # Checking that all the user account to add exist
    accounts_not_found = []
    for member in to_add:
        if module.get_account(member[0]) is None:
            accounts_not_found.append(member[0])
    if accounts_not_found:
        module.fail_json(
            msg="At least one user to add as team member does not exist: {users}.".format(
                users=", ".join(accounts_not_found)
            )
        )

    for perm in to_delete:
        module.delete(
            True,
            "user repository permission",
            perm[0],
            "repository/{full_repo_name}/permissions/user/{user}",
            auto_exit=False,
            full_repo_name=full_repo_name,
            user=perm[0],
        )
        changed = True

    for perm in to_add:
        module.unconditional_update(
            "user repository permission",
            perm[0],
            "repository/{full_repo_name}/permissions/user/{user}",
            {"role": perm[1]},
            full_repo_name=full_repo_name,
            user=perm[0],
        )
        changed = True

    module.exit_json(changed=changed)


if __name__ == "__main__":
    main()
