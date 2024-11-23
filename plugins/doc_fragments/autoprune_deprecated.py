# -*- coding: utf-8 -*-

# Copyright: (c) 2024 Hervé Quatremain <herve.quatremain@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    # Ansible Galaxy documentation fragment
    DOCUMENTATION = r"""
options:
  auto_prune_method:
    description:
      - The O(auto_prune_method) parameter is deprecated and will be removed in
        future versions of the collection.
        Use the M(infra.quay_configuration.quay_organization_prune) and the
        M(infra.quay_configuration.quay_repository_prune) modules instead.
      - Method to use for the auto-pruning tags policy.
      - If V(none), then the module ensures that no policy is in place. The
        tags are not pruned.
        If several policies are available, then the module removes them all.
      - If V(tags), then the policy keeps only the number of tags that you
        specify in O(auto_prune_value).
      - If V(date), then the policy deletes the tags older than the time period
        that you specify in O(auto_prune_value).
      - O(auto_prune_value) is required when O(auto_prune_method) is V(tags) or
        V(date).
    type: str
    choices: [none, tags, date]
  auto_prune_value:
    description:
      - The O(auto_prune_value) parameter is deprecated and will be removed in
        future versions of the collection.
        Use the M(infra.quay_configuration.quay_organization_prune) and the
        M(infra.quay_configuration.quay_repository_prune) modules instead.
      - Number of tags to keep when O(auto_prune_method) is V(tags).
        The value must be 1 or more.
      - Period of time when O(auto_prune_method) is V(date). The value must be 1
        or more, and must be followed by a suffix; s (for second), m (for
        minute), h (for hour), d (for day), or w (for week).
      - O(auto_prune_method) is required when O(auto_prune_value) is set.
    type: str
notes:
  - The O(auto_prune_method) and O(auto_prune_value) parameters are deprecated
    and will be removed in future versions of the collection.
    Use the M(infra.quay_configuration.quay_organization_prune) and the
    M(infra.quay_configuration.quay_repository_prune) modules instead.
  - Your Quay administrator must enable the auto-prune capability of your Quay
    installation (C(FEATURE_AUTO_PRUNE) in C(config.yaml)) to use the
    O(auto_prune_method) and O(auto_prune_value) parameters.
  - Using O(auto_prune_method) and O(auto_prune_value) requires Quay version
    3.11 or later.
"""
