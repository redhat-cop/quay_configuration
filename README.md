# Quay Container Registry Collection for Ansible

[![Sanity Test](https://github.com/redhat-cop/quay_configuration/actions/workflows/pre-commit-sanity.yml/badge.svg)](https://github.com/redhat-cop/quay_configuration/actions/workflows/pre-commit-sanity.yml)
[![Integration Test](https://github.com/redhat-cop/quay_configuration/actions/workflows/ansible-integration.yml/badge.svg)](https://github.com/redhat-cop/quay_configuration/actions/workflows/ansible-integration.yml)


The collection provides modules for managing your Quay Container Registry deployment.

## Included Content

After you install the collection, use the `ansible-doc` command to access the collection documentation.

### Modules

Run the `ansible-doc -l infra.quay_configuration` command to list the modules that the collection provides.
For accessing the documentation of a module, use the `ansible-doc infra.quay_configuration.<module-name>` command.

You can also access the documentation from [Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/infra/quay_configuration/docs/).

Name | Description
---: | :---
`quay_api_token` |          Create OAuth access tokens for accessing the Quay Container Registry API
`quay_application` |        Manage Quay Container Registry applications
`quay_default_perm` |       Manage Quay Container Registry default repository permissions
`quay_docker_token` |       Manage tokens for accessing Quay Container Registry repositories
`quay_first_user` |         Create the first user account
`quay_layer_info` |         Gather information about image layers in Quay Container Registry
`quay_manifest_label` |     Manage Quay Container Registry image manifest labels
`quay_manifest_label_info` | Gather information about manifest labels in Quay Container Registry
`quay_message` |            Manage Quay Container Registry global messages
`quay_notification` |       Manage Quay Container Registry repository notifications
`quay_organization` |       Manage Quay Container Registry organizations
`quay_organization_prune` | Manage auto-pruning policies for organizations and user namespaces
`quay_proxy_cache` |        Manage Quay Container Registry proxy cache configurations
`quay_quota` |              Manage Quay Container Registry organizations quota
`quay_repository` |         Manage Quay Container Registry repositories
`quay_repository_mirror` |  Manage Quay Container Registry repository mirror configurations
`quay_repository_prune` |   Manage auto-pruning policies for repositories
`quay_robot` |              Manage Quay Container Registry robot accounts
`quay_tag` |                Manage Quay Container Registry image tags
`quay_tag_info` |           Gather information about tags in a Quay Container Registry repository
`quay_team` |               Manage Quay Container Registry teams
`quay_team_ldap` |          Synchronize Quay Container Registry teams with LDAP groups
`quay_team_oidc` |          Synchronize Quay Container Registry teams with OIDC groups
`quay_user` |               Manage Quay Container Registry users


### Jinja2 Filters

Run the `ansible-doc -t filter -l infra.quay_configuration` command to list the filters that the collection provides.
For accessing the documentation of a filter, use the `ansible-doc -t filter infra.quay_configuration.<filter-name>` command.

Name | Description
---: | :---
`quay_docker_config` |  Build a Docker configuration in JSON format

### Roles

Run the `ansible-doc -t role -l infra.quay_configuration` command to list the roles that the collection provides.
For accessing the documentation of a role, use the `ansible-doc -t role infra.quay_configuration.<role-name>` command.

Name | Description
---: | :---
`quay_org` | Create and configure a Quay Container Registry organization

## Installing the Collection

Before using the Quay collection, install it by using the Ansible Galaxy command-line tool:

```bash
ansible-galaxy collection install infra.quay_configuration
```

As an alternative, you can declare the collection in a `collections/requirements.yml` file inside your Ansible project:

```yaml
---
collections:
  - name: infra.quay_configuration
```

Use the `ansible-galaxy collection install -r collections/requirements.yml` command to install the collection from this file.
If you manage your Ansible project in automation controller, then automation controller detects this `collections/requirements.yml` file, and automatically installs the collection.

You can also download the tar archive from [Ansible Galaxy](https://galaxy.ansible.com/infra/quay_configuration), and then manually install the collection.

See [Ansible -- Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.


## Using the Collection

The modules in the collection access Quay through its REST API.
The modules can connect to the API by using a username and a password, or by using an OAuth access token.

There are two ways to get an OAuth access token:

* Use the Quay Container Registry web UI.
* Use the `infra.quay_configuration.quay_first_user` Ansible module to create the first user account just after you installed Quay Container Registry.
  The module creates and then returns an OAuth access token for the user.
  This token is only valid for 2 hours and 30 minutes.


### Creating an OAuth Access Token by Using the Web UI

Before you can use the collection, you must generate an OAuth access token.
To do so, follow these steps:

1. Log in to the Quay Container Registry web UI.
2. Use an existing organization or create a new one.
3. In the organization, create an application.
4. In the application, select the `Generate Token` menu.
5. Select the permissions to associate to the token.
   To be able to use all the modules in the collection, select `Administer Organization`, `Administer Repositories`, `Create Repositories`, `Super User Access`, and `Administer User`.
6. Click `Generate Token`.
7. Copy and then paste the token string into the `quay_token` module parameter.

The OAuth access token is linked to the user account you use to create it.
Your user account needs to have superuser permissions for some modules to operate correctly.
For example, to manage user accounts, the `infra.quay_configuration.quay_user` module needs a token created by a user that have superuser permissions.

See the [Quay.io API](https://docs.quay.io/api/) documentation for more details.


### Getting an OAuth Access Token when Creating the First User

Just after you installed Quay Container Registry, and before you do anything else, you can create the first user and generate an OAuth access token for that user.

After this initial operation, you can create additional user accounts by using the `infra.quay_configuration.quay_user` module and generate OAuth access tokens for these additional accounts by using the `infra.quay_configuration.quay_api_token` module.

The following playbook example uses the `infra.quay_configuration.quay_first_user` module to create the first user:

```yaml
---
- name: Bootstrapping a fresh Quay Container Registry installation
  hosts: localhost

  tasks:
    # You must probably ensure that the user account you create, admin in this
    # example, has superuser permissions so that you can use the generated
    # token to create additional objects.
    # To give the user superuser permissions, add its name to the SUPER_USERS
    # section in the config.yaml file.
    - name: Ensure the initial user exists
      infra.quay_configuration.quay_first_user:
        username: admin
        email: admin@example.com
        password: S6tGwo13
        create_token: true
        quay_host: https://quay.example.com
        validate_certs: true
      register: result

    # The token is valid for 2 hours and 30 minutes
    - name: Display the generated OAuth access token
      debug:
        msg: "Access token: {{ result['access_token'] }}"

    # Using the OAuth access token to continue configuring Quay
    - name: Ensure the user exists
      infra.quay_configuration.quay_user:
        username: lvasquez
        email: lvasquez@example.com
        password: vs9mrD55NP
        state: present
        quay_token: "{{ result['access_token'] }}"
        quay_host: https://quay.example.com
        validate_certs: true
```

The requirements for the `infra.quay_configuration.quay_first_user` module are as follows:

* You must use Quay version 3.6 or later.
* You must enable the first user creation feature (`FEATURE_USER_INITIALIZE` in `config.yaml`).
* You must use the internal database for user authentication (`AUTHENTICATION_TYPE` to `Database` in `config.yaml` or `Internal Authentication` to `Local Database` in the configuration web UI).
* You probably want the first user to have superuser permissions.
  To do so, add this user account to the `SUPER_USERS` section in the `config.yaml` file.


### Grouping Common Module Parameters

When your play calls multiple modules from the collection, you can group common module parameters in the `module_defaults` section, under the `group/infra.quay_configuration.quay` subsection.
For example, instead of repeating the `quay_host`, `quay_username`, and `quay_password` parameters in each task, you can declare them at the top of your play:

```yaml
---
- name: Creating the development organization and the developers team
  hosts: localhost

  module_defaults:
    group/infra.quay_configuration.quay:
      quay_host: https://quay.example.com
      quay_username: admin
      quay_password: S6tGwo13

  tasks:
    - name: Ensure the organization exists
      infra.quay_configuration.quay_organization:
        name: development
        email: devorg@example.com
        time_machine_expiration: "1d"
        state: present

    - name: Ensure the additional user exists
      infra.quay_configuration.quay_user:
        username: dwilde
        email: dwilde@example.com
        password: 7BbB8T6c
        state: present

    - name: Ensure the team exists in the development organization
      infra.quay_configuration.quay_team:
        name: developers
        organization: development
        role: creator
        members:
          - lvasquez
          - dwilde
        append: false
        state: present
```


## Contributing to the Collection

We welcome community contributions to this collection.
If you find problems, then please open an [issue](https://github.com/redhat-cop/quay_configuration/issues) or create a [pull request](https://github.com/redhat-cop/quay_configuration/pulls).

More information about contributing can be found in the [Contribution Guidelines](https://github.com/redhat-cop/quay_configuration/blob/main/CONTRIBUTING.md).


## Release Notes

See the [changelog](https://github.com/redhat-cop/quay_configuration/blob/main/CHANGELOG.rst).


## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to read the full text.
