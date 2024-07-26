

.. meta::
  :antsibull-docs: 2.12.0


.. _plugins_in_infra.quay_configuration:

Infra.Quay_Configuration
========================

Collection version 2.0.0

.. contents::
   :local:
   :depth: 1

Description
-----------

Ansible modules to manage Quay Container Registry installations

**Authors:**

* Hervé Quatremain <rv4m@yahoo.co.uk>
* Tom Page <tpage@redhat.com>

**Supported ansible-core versions:**

* 2.15.0 or newer

.. ansible-links::

  - title: "Issue Tracker"
    url: "https://github.com/redhat-cop/quay_configuration/issues"
    external: true
  - title: "Repository (Sources)"
    url: "https://github.com/redhat-cop/quay_configuration"
    external: true




.. toctree::
    :maxdepth: 1

Plugin Index
------------

These are the plugins in the infra.quay_configuration collection:


Modules
~~~~~~~

* :ansplugin:`quay_api_token module <infra.quay_configuration.quay_api_token#module>` -- Create OAuth access tokens for accessing the Quay Container Registry API
* :ansplugin:`quay_application module <infra.quay_configuration.quay_application#module>` -- Manage Quay Container Registry applications
* :ansplugin:`quay_default_perm module <infra.quay_configuration.quay_default_perm#module>` -- Manage Quay Container Registry default repository permissions
* :ansplugin:`quay_docker_token module <infra.quay_configuration.quay_docker_token#module>` -- Manage tokens for accessing Quay Container Registry repositories
* :ansplugin:`quay_first_user module <infra.quay_configuration.quay_first_user#module>` -- Create the first user account
* :ansplugin:`quay_layer_info module <infra.quay_configuration.quay_layer_info#module>` -- Gather information about image layers in Quay Container Registry
* :ansplugin:`quay_manifest_label module <infra.quay_configuration.quay_manifest_label#module>` -- Manage Quay Container Registry image manifest labels
* :ansplugin:`quay_manifest_label_info module <infra.quay_configuration.quay_manifest_label_info#module>` -- Gather information about manifest labels in Quay Container Registry
* :ansplugin:`quay_message module <infra.quay_configuration.quay_message#module>` -- Manage Quay Container Registry global messages
* :ansplugin:`quay_notification module <infra.quay_configuration.quay_notification#module>` -- Manage Quay Container Registry repository notifications
* :ansplugin:`quay_organization module <infra.quay_configuration.quay_organization#module>` -- Manage Quay Container Registry organizations
* :ansplugin:`quay_proxy_cache module <infra.quay_configuration.quay_proxy_cache#module>` -- Manage Quay Container Registry proxy cache configurations
* :ansplugin:`quay_quota module <infra.quay_configuration.quay_quota#module>` -- Manage Quay Container Registry organizations quota
* :ansplugin:`quay_repository module <infra.quay_configuration.quay_repository#module>` -- Manage Quay Container Registry repositories
* :ansplugin:`quay_repository_mirror module <infra.quay_configuration.quay_repository_mirror#module>` -- Manage Quay Container Registry repository mirror configurations
* :ansplugin:`quay_robot module <infra.quay_configuration.quay_robot#module>` -- Manage Quay Container Registry robot accounts
* :ansplugin:`quay_tag module <infra.quay_configuration.quay_tag#module>` -- Manage Quay Container Registry image tags
* :ansplugin:`quay_tag_info module <infra.quay_configuration.quay_tag_info#module>` -- Gather information about tags in a Quay Container Registry repository
* :ansplugin:`quay_team module <infra.quay_configuration.quay_team#module>` -- Manage Quay Container Registry teams
* :ansplugin:`quay_team_ldap module <infra.quay_configuration.quay_team_ldap#module>` -- Synchronize Quay Container Registry teams with LDAP groups
* :ansplugin:`quay_team_oidc module <infra.quay_configuration.quay_team_oidc#module>` -- Synchronize Quay Container Registry teams with OIDC groups
* :ansplugin:`quay_user module <infra.quay_configuration.quay_user#module>` -- Manage Quay Container Registry users
* :ansplugin:`quay_vulnerability_info module <infra.quay_configuration.quay_vulnerability_info#module>` -- Gather information about image vulnerabilities in Quay Container Registry

.. toctree::
    :maxdepth: 1
    :hidden:

    quay_api_token_module
    quay_application_module
    quay_default_perm_module
    quay_docker_token_module
    quay_first_user_module
    quay_layer_info_module
    quay_manifest_label_module
    quay_manifest_label_info_module
    quay_message_module
    quay_notification_module
    quay_organization_module
    quay_proxy_cache_module
    quay_quota_module
    quay_repository_module
    quay_repository_mirror_module
    quay_robot_module
    quay_tag_module
    quay_tag_info_module
    quay_team_module
    quay_team_ldap_module
    quay_team_oidc_module
    quay_user_module
    quay_vulnerability_info_module


Filter Plugins
~~~~~~~~~~~~~~

* :ansplugin:`quay_docker_config filter <infra.quay_configuration.quay_docker_config#filter>` -- Build a Docker configuration in JSON format

.. toctree::
    :maxdepth: 1
    :hidden:

    quay_docker_config_filter


Role Index
----------

These are the roles in the infra.quay_configuration collection:

* :ansplugin:`quay_org role <infra.quay_configuration.quay_org#role>` -- Create and configure a Quay Container Registry organization


.. toctree::
    :maxdepth: 1
    :hidden:

    quay_org_role

