================================================
Quay Container Registry Collection Release Notes
================================================

.. contents:: Topics

v2.0.0
======

Release Summary
---------------

Renaming the ``herve4m.quay`` collection to ``infra.quay_configuration``, and moving the developments to a new GitHub repository (https://github.com/redhat-cop/quay_configuration).

Breaking Changes / Porting Guide
--------------------------------

- The name of the collection changes to ``infra.quay_configuration``.

v1.3.0
======

New Plugins
-----------

Filter
~~~~~~

- infra.quay_configuration.quay_docker_config - Build a Docker configuration in JSON format

v1.2.0
======

Minor Changes
-------------

- Add support for the auto-pruning tags feature in Quay 3.11 for organizations and repositories. The ``infra.quay_configuration.quay_organization`` and ``infra.quay_configuration.quay_repository`` modules now have the ``auto_prune_method`` and ``auto_prune_value`` options.

New Modules
-----------

- infra.quay_configuration.quay_team_oidc - Synchronize Quay Container Registry teams with OIDC groups

v1.1.0
======

v1.0.4
======

New Modules
-----------

- infra.quay_configuration.quay_proxy_cache - Manage Quay Container Registry proxy cache configurations

v1.0.3
======

Release Summary
---------------

Testing against Quay version 3.10.1.

v1.0.2
======

Release Summary
---------------

Testing against Quay version 3.9.1.

v1.0.1
======

Release Summary
---------------

Testing against Quay version 3.8.6.

Bugfixes
--------

- quay_user - Workaround empty SUPER_USERS configuration parameter. (https://github.com/redhat-cop/quay_configuration/issues/26)

v1.0.0
======

Release Summary
---------------

Testing against Quay version 3.8.5.

Bugfixes
--------

- quay_api_token - Convert response headers in lowercase. (https://github.com/redhat-cop/quay_configuration/issues/23)

v0.1.3
======

Release Summary
---------------

Testing against Quay version 3.8.0.

v0.1.2
======

Release Summary
---------------

Adding the ``infra.quay_configuration.quay`` module defaults group.

Minor Changes
-------------

- Add the ``infra.quay_configuration.quay`` module defaults group. To avoid repeating common parameters, such as ``quay_host`` or ``quay_token``, in each task, you can define these common module parameters at the top of your play, in the ``module_defaults`` section, under the ``group/infra.quay_configuration.quay`` subsection.

v0.1.1
======

Release Summary
---------------

Updating documentation and testing against version 3.7.2

v0.1.0
======

Minor Changes
-------------

- In addition to token authentication, the modules can now connect to the Quay API by using a login and password scheme. The new ``quay_username`` and ``quay_password`` parameters are mutually exclusive with the ``quay_token`` parameter.

v0.0.14
=======

Release Summary
---------------

Collection tested against Red Hat Quay v3.7.0

v0.0.13
=======

New Roles
---------

- infra.quay_configuration.quay_org - Create and configure a Red Hat Quay organization

v0.0.12
=======

New Modules
-----------

- infra.quay_configuration.quay_api_token - Create OAuth access tokens for accessing the Red Hat Quay API

v0.0.11
=======

New Modules
-----------

- infra.quay_configuration.quay_docker_token - Manage tokens for accessing Red Hat Quay repositories

v0.0.10
=======

New Modules
-----------

- infra.quay_configuration.quay_manifest_label - Manage Red Hat Quay image manifest labels
- infra.quay_configuration.quay_manifest_label_info - Gather information about manifest labels in Red Hat Quay

v0.0.9
======

New Modules
-----------

- infra.quay_configuration.quay_team_ldap - Synchronize Red Hat Quay teams with LDAP groups

v0.0.8
======

Minor Changes
-------------

- Tests - add integration tests.

Bugfixes
--------

- quay_notification - add a check to verify that the repository exists.

v0.0.7
======

Release Summary
---------------

New quay_first_user module

New Modules
-----------

- infra.quay_configuration.quay_first_user - Create the first user account

v0.0.6
======

Minor Changes
-------------

- quay_notification - add the ``vulnerability_level`` parameter.

v0.0.5
======

Release Summary
---------------

Collection tested against Red Hat Quay v3.6.1

v0.0.4
======

Release Summary
---------------

New quay_repository_mirror module

v0.0.3
======

Release Summary
---------------

New quay_vulnerability_info information module

v0.0.2
======

Release Summary
---------------

Fix wrong project URLs

v0.0.1
======

Release Summary
---------------

Initial public release.

New Modules
-----------

- infra.quay_configuration.quay_application - Manage Red Hat Quay organizations
- infra.quay_configuration.quay_default_perm - Manage Red Hat Quay default repository permissions
- infra.quay_configuration.quay_image_info - Gather information about images in a Red Hat Quay repository
- infra.quay_configuration.quay_message - Manage Red Hat Quay global messages
- infra.quay_configuration.quay_notification - Manage Red Hat Quay repository notifications
- infra.quay_configuration.quay_organization - Manage Red Hat Quay organizations
- infra.quay_configuration.quay_repository - Manage Red Hat Quay repositories
- infra.quay_configuration.quay_robot - Manage Red Hat Quay robot accounts
- infra.quay_configuration.quay_tag_info - Gather information about tags in a Red Hat Quay repository
- infra.quay_configuration.quay_team - Manage Red Hat Quay teams
- infra.quay_configuration.quay_user - Manage Red Hat Quay users
