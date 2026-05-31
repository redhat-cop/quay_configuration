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
module: quay_organization_mirror
short_description:
  Manage Quay Container Registry organization mirror configurations
description:
  - Configure and synchronize organization-level mirrors in
    Quay Container Registry.
  - Organization mirroring enables automatic synchronization of all repositories
    (or a filtered subset) from an external registry namespace into a Quay
    organization.
version_added: '2.8.0'
author: Hervé Quatremain (@herve4m)
options:
  organization:
    description:
      - Name of the organization to configure for mirroring.
      - The organization must exist and be empty (contain no repositories) when
        creating a new mirror configuration.
    required: true
    type: str
  state:
    description:
      - If V(absent), then the module deletes the organization mirror
        configuration.
      - If V(present), then the module creates the organization mirror
        configuration if it does not already exist, or update it if it exists.
    type: str
    default: present
    choices: [absent, present]
  is_enabled:
    description:
      - Defines whether the mirror configuration is active or inactive.
      - V(true) by default.
    type: bool
  external_registry_type:
    description:
      - Type of the external registry from which repositories are mirrored.
      - This parameter is required when creating the mirroring configuration.
      - The type cannot be changed after creation.
    type: str
    choices: [quay, harbor]
  external_registry_url:
    description:
      - URL of the external registry, such as https://quay.io or
        https://harbor.example.com
      - This parameter is required when creating the mirroring configuration.
    type: str
  external_namespace:
    description:
      - Namespace, or project, in the external registry from which repositories
        are mirrored, such as C(projectquay) or C(library).
      - This parameter is required when creating the mirroring configuration.
    type: str
  external_registry_username:
    description:
      - Username to use for pulling images from the remote registry.
      - If not provided, then anonymous access is used.
    type: str
  external_registry_password:
    description:
      - Password to use for pulling images from the remote registry.
      - Only used when O(external_registry_username) is also provided.
    type: str
  robot_username:
    description:
      - Username of the robot account that is used for synchronization.
      - The robot must belong to the organization specified in O(organization).
      - This parameter is required when creating the mirroring configuration.
    type: str
  visibility:
    description:
      - Visibility of the mirrored repositories created in the organization.
      - V(public) by default.
    type: str
    choices: [public, private]
  repository_filters:
    description:
      - List of repository name patterns to synchronize from the external
        namespace.
      - Supports glob patterns such as C(hello*), C(busy*), or C(*test).
      - If not specified or empty, then all repositories from the external
        namespace are synchronized.
    type: list
    elements: str
  sync_interval:
    description:
      - Synchronization interval for this repository mirror in seconds.
      - The O(sync_interval) parameter accepts a time unit as a suffix;
        C(s) for seconds, C(m) for minutes, C(h) for hours, C(d) for days, and
        C(w) for weeks. For example, C(8h) for eight hours.
      - The minimal value in 60 seconds.
      - 86400 (one day) by default.
    type: str
  sync_start_date:
    description:
      - The date and time at which the first synchronization should be
        initiated.
      - The format for the O(sync_start_date) parameter is ISO 8601 UTC, such
        as 2026-04-25T21:06:00Z.
      - If you do not provide the O(sync_start_date) parameter when you
        configure a new organization mirror, then the synchronization is
        immediately active, and a synchronization is initiated if the
        O(is_enabled) parameter is V(true).
    type: str
  skopeo_timeout:
    description:
      - Maximum duration of mirroring jobs.
      - The timeout must be between 5 minutes (300 seconds) and 12 hours
        (43200 seconds).
      - The O(skopeo_timeout) parameter accepts a time unit as a suffix;
        C(s) for seconds, C(m) for minutes, and C(h) for hours. For example,
        C(10m) for 10 minutes.
      - 5 minutes (300 seconds) by default.
    type: str
    aliases: [skopeo_timeout_interval]
  verify_tls:
    description:
      - Defines whether TLS of the external registry should be verified.
      - V(true) by default.
    type: bool
  http_proxy:
    description:
      - HTTP proxy to use for accessing the remote container registry.
      - See the C(curl) documentation for more details.
      - By default, no proxy is used.
    type: str
  https_proxy:
    description:
      - HTTPS proxy to use for accessing the remote container registry.
      - See the C(curl) documentation for more details.
      - By default, no proxy is used.
    type: str
  no_proxy:
    description:
      - Comma-separated list of hosts for which the proxy should not be used.
      - Only relevant when you also specify a proxy configuration by setting
        the O(http_proxy) or O(https_proxy) variables.
      - See the C(curl) documentation for more details.
    type: str
  force_sync:
    description:
      - Triggers an immediate synchronization of all repositories in the mirror.
    type: bool
    default: false
notes:
  - The module requires Quay version 3.17 or later.
  - Your Quay administrator must enable the organization mirroring capability
    of your Quay installation (C(FEATURE_ORG_MIRROR) in C(config.yaml)) to use
    this module.
  - You cannot configure organization-level mirroring on an organization that
    already contains repositories. You must create a dedicated organization
    specifically to serve as a mirror target, with all repositories within the
    organization managed exclusively by the mirroring configuration.
  - You cannot modify an organization mirroring configuration if a
    synchronization is in progress.
  - The user account associated with the token that you provide in O(quay_token)
    must have administrator access to the organization.
  - You cannot change the O(external_registry_type) parameter after you create
    the mirror configuration.
  - See the M(infra.quay_configuration.quay_repository_mirror) module
    to mirror a single repository.
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
- name: Ensure organization mirroring is configured for mirror-org
  infra.quay_configuration.quay_organization_mirror:
    organization: mirror-org
    external_registry_type: quay
    external_registry_url: https://quay.io
    external_namespace: projectquay
    robot_username: mirror-org+syncrobot
    visibility: public
    repository_filters:
      - quay
      - clair
      - redis
    sync_interval: 2d
    sync_start_date: "2026-04-27T13:00:00Z"
    is_enabled: true
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure organization mirroring uses authenticated access
  infra.quay_configuration.quay_organization_mirror:
    organization: mirror-org
    external_registry_username: myuser
    external_registry_password: mypassword
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure organization mirroring is disabled
  infra.quay_configuration.quay_organization_mirror:
    organization: mirror-org
    is_enabled: false
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Trigger an immediate synchronization
  infra.quay_configuration.quay_organization_mirror:
    organization: mirror-org
    force_sync: true
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7

- name: Ensure the organization mirror configuration is removed
  infra.quay_configuration.quay_organization_mirror:
    organization: mirror-org
    state: absent
    quay_host: https://quay.example.com
    quay_token: vgfH9zH5q6eV16Con7SvDQYSr0KPYQimMHVehZv7
"""

RETURN = r""" # """

import copy
from datetime import datetime

from ..module_utils.api_module import APIModule


def main():
    argument_spec = dict(
        organization=dict(required=True),
        state=dict(choices=["present", "absent"], default="present"),
        is_enabled=dict(type="bool"),
        external_registry_type=dict(choices=["quay", "harbor"]),
        external_registry_url=dict(),
        external_namespace=dict(),
        external_registry_username=dict(),
        external_registry_password=dict(no_log=True),
        robot_username=dict(),
        visibility=dict(choices=["public", "private"]),
        repository_filters=dict(type="list", elements="str"),
        sync_interval=dict(type="str"),
        sync_start_date=dict(),
        skopeo_timeout=dict(type="str", aliases=["skopeo_timeout_interval"]),
        verify_tls=dict(type="bool"),
        http_proxy=dict(),
        https_proxy=dict(),
        no_proxy=dict(),
        force_sync=dict(type="bool", default=False),
    )

    # Create a module for ourselves
    module = APIModule(argument_spec=argument_spec, supports_check_mode=True)

    # Extract our parameters
    organization = module.params.get("organization")
    state = module.params.get("state")
    is_enabled = module.params.get("is_enabled")
    external_registry_type = module.params.get("external_registry_type")
    external_registry_url = module.params.get("external_registry_url")
    external_namespace = module.params.get("external_namespace")
    external_registry_username = module.params.get("external_registry_username")
    external_registry_password = module.params.get("external_registry_password")
    robot_username = module.params.get("robot_username")
    visibility = module.params.get("visibility")
    repository_filters = module.params.get("repository_filters")
    sync_interval = module.params.get("sync_interval")
    sync_start_date = module.params.get("sync_start_date")
    skopeo_timeout = module.params.get("skopeo_timeout")
    verify_tls = module.params.get("verify_tls")
    http_proxy = module.params.get("http_proxy")
    https_proxy = module.params.get("https_proxy")
    no_proxy = module.params.get("no_proxy")
    force_sync = module.params.get("force_sync")

    # Verify that the interval is valid and convert it to an integer (seconds)
    s_interval = (
        module.str_period_to_second("sync_interval", sync_interval)
        if sync_interval is not None
        else 86400
    )
    if s_interval < 60:
        module.fail_json(
            msg=(
                "Wrong value for the `sync_interval` parameter: {value} ({value_s}s) is "
                "lower than 60 seconds"
            ).format(value=sync_interval, value_s=s_interval)
        )
    s_timeout = (
        module.str_period_to_second("skopeo_timeout", skopeo_timeout)
        if skopeo_timeout is not None
        else 300
    )
    if s_timeout < 300 or s_timeout > 43200:
        module.fail_json(
            msg=(
                "Wrong value for the `skopeo_timeout` parameter: {value} ({value_s}s) is "
                "not between 5 minutes (300s) and 12 hours (43200s)"
            ).format(value=skopeo_timeout, value_s=s_timeout)
        )

    if not module.get_organization(organization):
        if state == "absent":
            module.exit_json(changed=False)
        module.fail_json(
            msg="The {orgname} organization does not exist.".format(orgname=organization)
        )

    # Get the organization mirror configuration details
    #
    # GET /api/v1/organization/{orgname}/mirror
    # {
    #   "is_enabled": true,
    #   "external_registry_type": "quay",
    #   "external_registry_url": "https://quay.io",
    #   "external_namespace": "lib",
    #   "external_registry_username": "...",
    #   "has_external_registry_password": true,
    #   "external_registry_config": {
    #     "verify_tls": true,
    #     "proxy": {
    #       "http_proxy": null,
    #       "https_proxy": null,
    #       "no_proxy": null
    #     }
    #   },
    #   "repository_filters": ["hello*", "busy*"],
    #   "robot_username": "org1+myrobot",
    #   "visibility": "public",
    #   "sync_interval": 604800,
    #   "sync_start_date": "2026-04-25T16:00:00Z",
    #   "sync_expiration_date": null,
    #   "sync_status": "NEVER_RUN",
    #   "sync_retries_remaining": 3,
    #   "repo_sync_status_counts": {
    #     "CANCEL": 0,
    #     "FAIL": 0,
    #     "NEVER_RUN": 0,
    #     "SUCCESS": 0,
    #     "SYNCING": 0,
    #     "SYNC_NOW": 0,
    #     "SKIP": 0
    #   },
    #   "skopeo_timeout": 451,
    #   "creation_date": "2026-04-23T14:09:52.950894Z"
    # }

    mirror_details = module.get_object_path(
        "organization/{organization}/mirror",
        ok_error_codes=[404],
        organization=organization,
    )

    # Remove the mirror configuration
    if state == "absent":
        module.delete(
            mirror_details,
            "organization mirror configuration",
            organization,
            "organization/{organization}/mirror",
            organization=organization,
        )

    # Create a new synchronization configuration
    if not mirror_details:
        # Verify the mandatory parameters for creation
        missing_req_params = []
        if external_registry_type is None:
            missing_req_params.append("external_registry_type")
        if external_registry_url is None:
            missing_req_params.append("external_registry_url")
        if external_namespace is None:
            missing_req_params.append("external_namespace")
        if robot_username is None:
            missing_req_params.append("robot_username")
        if missing_req_params:
            module.fail_json(
                msg="missing required arguments: {args}".format(
                    args=", ".join(missing_req_params)
                )
            )

        # Create the organization mirror configuration
        new_fields = {
            "is_enabled": is_enabled if is_enabled is not None else True,
            "external_registry_type": external_registry_type,
            "external_registry_url": external_registry_url,
            "external_namespace": external_namespace,
            "robot_username": robot_username,
            "visibility": visibility if visibility else "public",
            "sync_interval": s_interval,
            "sync_start_date": (
                sync_start_date
                if sync_start_date
                else datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            ),
            "external_registry_config": {
                "verify_tls": verify_tls if verify_tls is not None else True,
                "proxy": {
                    "http_proxy": http_proxy if http_proxy else None,
                    "https_proxy": https_proxy if https_proxy else None,
                    "no_proxy": no_proxy if no_proxy else None,
                },
            },
            "repository_filters": repository_filters if repository_filters else [],
            "skopeo_timeout": s_timeout,
            "external_registry_username": (
                external_registry_username if external_registry_username else None
            ),
            "external_registry_password": (
                external_registry_password if external_registry_password else None
            ),
        }

        module.create(
            "organization mirror configuration",
            organization,
            "organization/{organization}/mirror",
            new_fields,
            auto_exit=False,
            organization=organization,
        )

        if force_sync:
            module.create(
                "organization mirror configuration",
                organization,
                "organization/{organization}/mirror/sync-now",
                {},
                auto_exit=False,
                organization=organization,
            )

        module.exit_json(changed=True)

    # Update the organization mirror configuration
    new_fields = {}
    if external_registry_password is not None:
        new_fields["external_registry_password"] = external_registry_password
    if external_registry_username is not None:
        new_fields["external_registry_username"] = external_registry_username
    if sync_start_date is not None:
        new_fields["sync_start_date"] = sync_start_date
    if sync_interval is not None:
        new_fields["sync_interval"] = s_interval
    if skopeo_timeout is not None:
        new_fields["skopeo_timeout"] = s_timeout
    if robot_username is not None:
        new_fields["robot_username"] = robot_username
    if external_registry_url is not None:
        new_fields["external_registry_url"] = external_registry_url
    if external_namespace is not None:
        new_fields["external_namespace"] = external_namespace
    if is_enabled is not None:
        new_fields["is_enabled"] = is_enabled
    if visibility is not None:
        new_fields["visibility"] = visibility
    if repository_filters is not None:
        new_fields["repository_filters"] = repository_filters

    try:
        registry_config = copy.deepcopy(mirror_details["external_registry_config"])
    except KeyError:
        registry_config = {}
    if verify_tls is not None:
        registry_config["verify_tls"] = verify_tls
    if http_proxy is not None:
        if "proxy" not in registry_config:
            registry_config["proxy"] = {}
        registry_config["proxy"]["http_proxy"] = http_proxy if http_proxy else None
    if https_proxy is not None:
        if "proxy" not in registry_config:
            registry_config["proxy"] = {}
        registry_config["proxy"]["https_proxy"] = https_proxy if https_proxy else None
    if no_proxy is not None:
        if "proxy" not in registry_config:
            registry_config["proxy"] = {}
        registry_config["proxy"]["no_proxy"] = no_proxy if no_proxy else None
    if registry_config:
        new_fields["external_registry_config"] = registry_config

    changed = False
    if new_fields:
        # Cannot update the configuration when a synchronization is in progress
        if mirror_details.get("sync_status") == "SYNCING":
            module.exit_json(
                skipped=True,
                msg="cannot update the configuration while a synchronization is in progress",
            )
        updated, _not_used = module.update(
            mirror_details,
            "organization mirror configuration",
            organization,
            "organization/{organization}/mirror",
            new_fields,
            auto_exit=False,
            organization=organization,
        )
        if updated:
            changed = True

    if force_sync and mirror_details.get("sync_status") not in ("SYNCING", "SYNC_NOW"):
        module.create(
            "organization mirror configuration",
            organization,
            "organization/{organization}/mirror/sync-now",
            {},
            auto_exit=False,
            organization=organization,
        )
        changed = True

    module.exit_json(changed=changed)


if __name__ == "__main__":
    main()
