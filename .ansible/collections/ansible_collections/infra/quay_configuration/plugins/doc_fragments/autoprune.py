# -*- coding: utf-8 -*-

# Copyright: (c) 2024 Hervé Quatremain <herve.quatremain@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    # Ansible Galaxy documentation fragment
    DOCUMENTATION = r"""
options:
  method:
    description:
      - Method to use for the auto-pruning tags policy.
      - If V(tags), then the policy keeps only the number of tags that you
        specify in O(value).
      - If V(date), then the policy deletes the tags older than the time period
        that you specify in O(value).
    required: true
    type: str
    choices: [tags, date]
  value:
    description:
      - Number of tags to keep when O(method) is V(tags).
        The value must be 1 or more.
      - Period of time when O(method) is V(date). The value must be 1 or more,
        and must be followed by a suffix; s (for second), m (for minute), h
        (for hour), d (for day), or w (for week).
    required: true
    type: str
  tag_pattern:
    description:
      - Regular expression to select the tags to process.
      - If you do not set the parameter, then Quay processes all the tags.
    type: str
  tag_pattern_matches:
    description:
      - If V(true), then Quay processes the tags matching the O(tag_pattern)
        parameter.
      - If V(false), then Quay excludes the tags matching the O(tag_pattern)
        parameter.
      - V(true) by default.
    type: bool
    default: true
notes:
  - Your Quay administrator must enable the auto-pruning capability of your
    Quay installation (C(FEATURE_AUTO_PRUNE) in C(config.yaml)).
  - Auto-pruning requires Quay version 3.13 or later.
"""
