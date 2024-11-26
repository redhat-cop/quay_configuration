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
#
# Notes:
#  - You cannot rename robot accounts.
#  - You cannot update the description of robot accounts.
#  - The current user can create/delete robot accounts in their personal
#    namespace, but not in the namespace of other users.

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: quay_robot
short_description: Manage Quay Container Registry robot accounts
description:
  - Create and delete robot accounts.
version_added: '0.0.1'
author: Hervé Quatremain (@herve4m)
options:
  name:
    description:
      - Name of the robot account to create or remove, in the format
        C(namespace)+C(shortname). The namespace can be an organization or your
        personal namespace.
      - The short name (the part after the C(+) sign) must be in lowercase,
        must not contain white spaces, must not start by a digit, and must be
        at least two characters long.
      - If you omit the namespace part in the name, then the module uses your
        personal namespace.
      - You can create and delete robot accounts in your personal namespace,
        but not in the personal namespace of other users. The token you use in
        O(quay_token) determines the user account you are using.
    required: true
    type: str
  description:
    description:
      - Description of the robot account. You cannot update the description
        of existing robot accounts.
    type: str
  federations:
    description:
      - Federation configurations, which enable keyless authentication with
        robot accounts.
      - Robot account federations require Quay version 3.13 or later.
    type: list
    elements: dict
    suboptions:
      issuer:
        description:
          - OpenID Connect (OIDC) issuer URL.
        required: true
        type: str
      subject:
        description:
          - OpenID Connect (OIDC) subject.
        required: true
        type: str
  append:
    description:
      - If V(true), then add the robot account federation configurations
        defined in O(federations).
      - If V(false), then the module sets the federation configurations
        specified in O(federations), removing all others federation
        configurations.
      - Robot account federations require Quay version 3.13 or later.
    type: bool
    default: true
  state:
    description:
      - If V(absent), then the module deletes the robot account.
      - The module does not fail if the account does not exist, because the
        state is already as expected.
      - If V(present), then the module creates the robot account if it does not
        already exist.
    type: str
    default: present
    choices: [absent, present]
notes:
  - The token that you provide in O(quay_token) must have the "Administer
    Organization" and "Administer User" permissions.
  - The O(federations) and O(append) parameters require Quay version 3.13 or
    later.
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
- name: Ensure the robot account production+robotprod1 exists
  infra.quay_configuration.quay_robot:
    name: production+robotprod1
    description: Robot account for production
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7
  register: robot_details

- ansible.builtin.debug:
    msg: "Robot token: {{ robot_details['token'] }}"

- ansible.builtin.debug:
    msg: "Docker configuration (Base64): {{ robot_details['name']
      | infra.quay_configuration.quay_docker_config(robot_details['token'],
      'https://quay.example.com') }}"

- name: Ensure the robot account myrobot exists in my namespace
  infra.quay_configuration.quay_robot:
    name: myrobot
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure the robot account production+robotdev1 does not exists
  infra.quay_configuration.quay_robot:
    name: production+robotdev1
    state: absent
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

# Robot account federations require Quay version 3.13 or later
- name: Ensure the robot account production+robotprod2 exists, with federation
  infra.quay_configuration.quay_robot:
    name: production+robotprod2
    description: Second robot account for production
    federations:
      - issuer: https://keycloak-auth-realm.quayadmin.org/realms/quayrealm
        subject: 449e14f8-9eb5-4d59-a63e-b7a77c75f770
    state: present
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7
"""

RETURN = r"""
name:
  description:
    - Token name.
    - From this name and the token, in RV(token), you can construct a Docker
      configuration file that you can use to manage images in the container
      image registry. See P(infra.quay_configuration.quay_docker_config#filter).
  returned: changed
  type: str
  sample: production+robotprod1
token:
  description: Robot credential (token).
  returned: changed
  type: str
  sample: IWG3K5EW92KZLPP42PMOKM5CJ2DEAQMSCU33A35NR7MNL21004NKVP3BECOWSQP2
"""

import json

from ..module_utils.api_module import APIModule


def exit_module(module, changed, data):
    """Exit the module and return data.

    :param module: The module object.
    :type module: :py:class:``APIModule``
    :param changed: The changed status of the object.
    :type changed: bool
    :param data: The data returned by the API call.
    :type data: dict
    """
    result = {"changed": changed}
    if data:
        if "name" in data:
            result["name"] = data["name"]
        if "token" in data:
            result["token"] = data["token"]
    module.exit_json(**result)


def main():
    argument_spec = dict(
        name=dict(required=True),
        description=dict(),
        federations=dict(
            type="list",
            elements="dict",
            options=dict(
                issuer=dict(required=True),
                subject=dict(required=True),
            ),
        ),
        append=dict(type="bool", default=True),
        state=dict(choices=["present", "absent"], default="present"),
    )

    # Create a module for ourselves
    module = APIModule(argument_spec=argument_spec, supports_check_mode=True)

    # Extract our parameters
    name = module.params.get("name")
    description = module.params.get("description")
    federations = module.params.get("federations")
    append = module.params.get("append")
    state = module.params.get("state")

    namespace, robot_shortname, is_org = module.split_name("name", name, state, separator="+")

    # Build the API URL to access the robot object.
    if is_org:
        path_url = "organization/{orgname}/robots/{robot_shortname}".format(
            orgname=namespace, robot_shortname=robot_shortname
        )
    else:
        path_url = "user/robots/{robot_shortname}".format(robot_shortname=robot_shortname)

    fed_url = "{url}/federation".format(url=path_url)
    fed_req_set = (
        set([(f.get("issuer"), f.get("subject")) for f in federations])
        if federations
        else set()
    )

    # Get the robot account details.
    #
    # For robot accounts in organizations:
    #
    # GET /api/v1/organization/{orgname}/robots/{robot_shortname}
    # {
    #   "name": "production+robot1",
    #   "created": "Sun, 26 Sep 2021 14:22:14 -0000",
    #   "last_accessed": null,
    #   "description": "Robot for the production environment",
    #   "token": "D69U...TQT6",
    #   "unstructured_metadata": {}
    # }
    #
    # For robot accounts for the current user:
    #
    # GET /api/v1/user/robots/{robot_shortname}
    # {
    #   "name": "operator1+monrobot",
    #   "created": "Sun, 26 Sep 2021 14:33:43 -0000",
    #   "last_accessed": null,
    #   "description": "Robot for my personal namespace",
    #   "token": "EUF6...X0MU",
    #   "unstructured_metadata": {}
    # }
    robot_details = module.get_object_path(path_url, ok_error_codes=[400, 404])

    # Remove the robot account
    if state == "absent":
        module.delete(robot_details, "robot account", name, path_url)

    if robot_details:
        # GET /api/v1/organization/{orgname}/robots/{robot_shortname}/federation
        # [
        #   {
        #     "issuer": "https://keycloak-realm.quayadmin.org/realms/quayrealm",
        #     "subject": "449e14f8-9eb5-4d59-a63e-b7a77c75f770"
        #   }
        # ]
        fed_details = module.get_object_path(fed_url)
        fed_curr_set = (
            set([(f.get("issuer"), f.get("subject")) for f in fed_details])
            if fed_details
            else set()
        )
        fed_to_add = fed_req_set - fed_curr_set

        if federations is None or fed_req_set == fed_curr_set or (append and not fed_to_add):
            exit_module(module, False, robot_details)

        if append:
            new_fields = [
                {"issuer": f[0], "subject": f[1], "isExpanded": False}
                for f in fed_req_set | fed_curr_set
            ]
        else:
            new_fields = [
                {"issuer": f[0], "subject": f[1], "isExpanded": False} for f in fed_req_set
            ]
        data = json.dumps(new_fields).encode()
        module.create("robot account federation", name, fed_url, data, auto_exit=False)
        exit_module(module, True, robot_details)

    # Prepare the data that gets set for create
    new_fields = {}
    if description:
        new_fields["description"] = description

    robot_data = module.unconditional_update("robot account", name, path_url, new_fields)
    if federations:
        new_fields = [
            {"issuer": f.get("issuer"), "subject": f.get("subject"), "isExpanded": False}
            for f in federations
        ]
        data = json.dumps(new_fields).encode()
        module.create("robot account federation", name, fed_url, data, auto_exit=False)
    exit_module(module, True, robot_data)


if __name__ == "__main__":
    main()
