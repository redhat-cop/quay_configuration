#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022-2024 Hervé Quatremain <herve.quatremain@redhat.com>
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
module: quay_api_token
short_description: Create OAuth access tokens for accessing the Quay Container Registry API
description: Create OAuth access tokens for authenticating with the API.
version_added: '0.0.12'
author: Hervé Quatremain (@herve4m)
options:
  quay_username:
    description:
      - The username to use for authenticating against the API.
      - If you do not set the parameter, then the module tries the
        E(QUAY_USERNAME) environment variable.
    type: str
    required: true
  quay_password:
    description:
      - The password to use for authenticating against the API.
      - If you do not set the parameter, then the module tries the
        E(QUAY_PASSWORD) environment variable.
    type: str
    required: true
  client_id:
    description:
      - The client ID associated with the OAuth application to use for
        generating the OAuth access token.
      - See the M(infra.quay_configuration.quay_application) module to create
        an application object and to retrieve the associated client ID.
    required: true
    type: str
  rights:
    description:
      - List of permissions to grant to the user account. V(all) means all the
        permissions.
    type: list
    elements: str
    choices:
      - org:admin
      - repo:admin
      - repo:create
      - repo:read
      - repo:write
      - super:user
      - user:admin
      - user:read
      - all
    default: repo:read
  for_user:
    description:
      - The username to generate an OAuth access token for.
      - The user receives a notification in the web interface, which enables
        the user to retrieve the token.
      - When you use this option, the module does not return the token.
      - Requires Quay version 3.12 or later.
    type: str
    required: false
notes:
  - O(for_user) requires Quay version 3.12 or later.
  - Your Quay administrator must enable the OAuth assignment capability
    of your Quay installation (C(FEATURE_ASSIGN_OAUTH_TOKEN) in C(config.yaml))
    to use the O(for_user) option in Quay version 3.12 or later.
  - The generated OAuth access token acts on behalf of the user account you use
    with the module (in O(for_user) if set, otherwise in O(quay_username)).
  - The user must have admin rights to the application's organization, by being
    the creator of this organization, or by belonging to a team with admin
    rights.
  - The module is not idempotent. Every time you run it, an additional OAuth
    access token is produced. The other OAuth access tokens stay valid.
  - You cannot delete OAuth access tokens.
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
- name: Generate an OAuth access token
  infra.quay_configuration.quay_api_token:
    quay_username: lvasquez
    quay_password: vs9mrD55NP
    # The OAuth application must exist, and the user must have admin rights
    # to the organization that hosts the application. See the following example
    # that shows how to create an organization, a team, and an application.
    client_id: PZ6F80R1LCVPGYNZGSZQ
    rights:
      - org:admin
      - user:admin
    quay_host: https://quay.example.com
  register: token_details

- name: Display the new OAuth access token
  ansible.builtin.debug:
    msg: "The OAuth access token is: {{ token_details['access_token'] }}"

- name: Generate an OAuth access token for dwilde
  infra.quay_configuration.quay_api_token:
    quay_username: lvasquez
    quay_password: vs9mrD55NP
    # A notification in the web interface informs dwilde of the new OAuth
    # access token.
    for_user: dwilde
    client_id: PZ6F80R1LCVPGYNZGSZQ
    rights:
      - repo:admin
    quay_host: https://quay.example.com

# The following example creates an organization, an OAuth application, a user
# account, and a team, and then generates an OAuth access token for this user
# account.
# The team grants organization admin rights to the user.
# The OAuth access token of an existing super user is required to create the
# organization, the application, the user account, and the team.
- name: Ensure the organization exists
  infra.quay_configuration.quay_organization:
    name: production
    email: prodlist@example.com
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure the extapp application exists
  infra.quay_configuration.quay_application:
    organization: production
    name: extapp
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7
  register: app_details

- name: Ensure the user exists
  infra.quay_configuration.quay_user:
    username: jziglar
    password: i45fR38GhY
    email: jziglar@example.com
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure the operators team exists in the production organization
  infra.quay_configuration.quay_team:
    name: operators
    organization: production
    role: admin
    members:
      - jziglar
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Generate an OAuth access token for the user
  infra.quay_configuration.quay_api_token:
    quay_username: jziglar
    quay_password: i45fR38GhY
    client_id: "{{ app_details['client_id'] }}"
    rights:
      - all
    quay_host: https://quay.example.com
  register: token_details

- name: Display the new OAuth access token
  ansible.builtin.debug:
    msg: "The OAuth access token is: {{ token_details['access_token'] }}"
"""

RETURN = r"""
access_token:
  description: The OAuth access token.
  returned: only when O(for_user) is not set
  type: str
  sample: CywbRGkh1ttYkRRy9VL0Aw0yU9q7J62vIeo7WCFw
 """

import re

from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.basic import env_fallback
from ..module_utils.api_module import APIModuleNoAuth, APIModuleError


def main():
    allowed_rights = [
        "org:admin",
        "repo:admin",
        "repo:create",
        "repo:read",
        "repo:write",
        "super:user",
        "user:admin",
        "user:read",
        "all",
    ]
    argument_spec = dict(
        quay_username=dict(required=True, fallback=(env_fallback, ["QUAY_USERNAME"])),
        quay_password=dict(
            required=True, no_log=True, fallback=(env_fallback, ["QUAY_PASSWORD"])
        ),
        client_id=dict(required=True),
        rights=dict(
            type="list", elements="str", choices=allowed_rights, default=["repo:read"]
        ),
        for_user=dict(),
    )

    # Create a module for ourselves
    module = APIModuleNoAuth(argument_spec=argument_spec, supports_check_mode=True)

    # Extract our parameters
    client_id = module.params.get("client_id")
    rights = module.params.get("rights")
    if not rights:
        module.fail_json(msg="argument cannot be empty: rights")
    if "all" in rights:
        rights = set(allowed_rights)
        rights.remove("all")
    else:
        rights = set(rights)
    for_user = module.params.get("for_user")

    redirect_url = module.host_url._replace(path="/oauth/localapp")
    data = {
        "response_type": "token",
        "client_id": client_id,
        "redirect_uri": redirect_url.geturl(),
        "scope": " ".join(rights),
    }

    # Generate an OAuth token for another user
    if for_user is not None:
        if module.check_mode:
            module.exit_json(changed=True)
        data["username"] = for_user
        # The data is provided as URL query parameters
        url = module.host_url._replace(path="/oauth/authorize/assignuser")._replace(
            query=urlencode(data)
        )
        try:
            response = module.make_raw_request("POST", url)
        except APIModuleError as e:
            module.fail_json(msg=str(e))

        if response["status_code"] != 200:
            module.fail_json(
                msg=(
                    "Cannot create the OAuth access token for {user}: "
                    "Maybe the user does not exist."
                ).format(user=for_user)
            )

        module.exit_json(changed=True)

    # Generate an OAuth token for the current user
    if module.check_mode:
        module.exit_json(
            changed=True, access_token="NotValidCheckModeNotValidCheckModeNotVal"
        )
    data["_csrf_token"] = module.token
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    url = module.host_url._replace(path="/oauth/authorizeapp")
    try:
        response = module.make_raw_request(
            "POST",
            url,
            ok_error_codes=[302],
            headers=headers,
            data=urlencode(data),
            follow_redirects=False,
        )
    except APIModuleError as e:
        module.fail_json(msg=str(e))

    # Depending on the Quay version the headers might not be in lowercase
    headers_lower = dict((k.lower(), v) for k, v in response["headers"].items())
    if "location" not in headers_lower:
        module.fail_json(msg="Cannot retrieve the OAuth access token from the returned data")

    try:
        token = re.search("access_token=(.*?)&", headers_lower["location"]).group(1)
    except AttributeError:
        module.fail_json(msg="Cannot retrieve the CSRF token from the returned data")

    module.exit_json(changed=True, access_token=token)


if __name__ == "__main__":
    main()
