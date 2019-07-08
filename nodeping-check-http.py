#!/usr/bin/env python3
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: nodeping-check-http
version_added: "0.0.1"
short_description: Module for manage http checks in NodePing
description:
    -  Module for manage http checks in NodePing
author:
    - Alexander Akulov (https://github.com/AlexAkulov)
 requirements:
    - "python >= 3.0"
options:
    label:
        description:
            -
        required: true
        type: str
        aliases: ["name"]
    enabled:
        description:
            -
        required: false
        default: true
        type: bool
    state:
        description:
            -
        required: false
        default: "present"
        choices: [ "present", "absent" ]
    description:
        description:
            -
        required: false
        default: ""
        type: str
    public_results:
        description:
            -
        required: false
        default: false
        type: bool
    region:
        description:
            - This causes the checks to be originated in the specified region. Usually it should be the region in which the server being monitored is located.
        required: false
        default: default
        type: str
        choices:
            - default
            - north america
            - europe
            - east asia/oceania
            - latin america
            - world wide
    frequency:
        description:
            -
        required: false
        default: 5m
        type: str
        choices:
            - 1m
            - 3m
            - 5m
            - 15m
            - 30m
            - 1h
            - 4h
            - 6h
            - 12h
            - 1d
    url:
        description:
            - HTTP or HTTPS URL in the form (http|https)://host.domain[:port]/path
        required: true
        type: str
    force_ipv6_resolution:
        description:
            - Forces IPv6 resolution for the FQDN in the URL. If you're unsure, use the (Default IP resolution).
        required: false
        default: false
        type: bool
    follow_redirects:
        description:
            - Whether or not the URI module should follow redirects.
        required: false
        default: false
        type: bool
    timeout:
        description:
            - Time in seconds for an acceptable response.
        required: false
        default: 5
        type: int
    sensitivity:
        description:
            - Rechecks help avoid unnecessary notifications. For most services we recommend "high"
        required: false
        default: high
        type: str
        choices:
            - very high
            - high
            - medium
            - low
            - very low
    notifications:
        description:
            -
        required: false
        default: []
        type: array
'''

EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_approle_role_secret_create:
        name: 'ashley'
      register: 'vault_approle_role_secret_create'
    - debug: msg="Role secret id is {{vault_approle_role_secret_create.id}}"
- hosts: localhost
  tasks:
    - hashivault_approle_role_secret_create:
        name: 'robert'
        secret_id: '{{ lookup("password", "/dev/null length=32 chars=ascii_letters,digits") }}'
      register: 'vault_approle_role_custom_secret_create'
    - debug: msg="Role custom secret id is {{vault_approle_role_custom_secret_create.id}}"
'''
from urllib.request import urlopen

from ansible.module_utils.basic import AnsibleModule
import sys
sys.path.append('./')

# from urllib import urlopen

from nodeping_api import get_checks

# from ansible.module_utils.basic import *
# from ansible.module_utils.urls import *


def check_exists(exsists_checks, label):
    return True

def has_different(exsists_checks, module):
    return True

def main():
    module = AnsibleModule(
        argument_spec=dict(
            label=dict(type='str', aliases=['name'], required=True),
            token=dict(type='str', required=True),
            enabled=dict(type='bool', required=False, default=True),
            state=dict(type='str', required=False, default='present', choices=['present', 'absent']),
            description=dict(type='str', required=False),
            public_results=dict(type='bool', required=False, default=False),
            region=dict(type='str', required=False, default='default', choices=['default', 'north america', 'europe', 'east asia/oceania', 'latin america', 'world wide']),
            frequency=dict(type='str', required=False, default='5m', choices=['1m', '3m', '5m', '15m', '30m', '1h', '4h', '6h', '12h', '1d']),
            url=dict(type='str', required=True),
            force_ipv6_resolution=dict(type='bool', required=False, default=False),
            follow_redirects=dict(type='bool', required=False, default=True),
            timeout=dict(type='int', required=False, default=5),
            sensitivity=dict(type='str', required=False, default='high', choices=['very high', 'high', 'medium', 'low', 'very low']),
            notifications=dict(type='array')
        )
    )
    checks_list = get_checks.GetChecks(module.params['token']).all_checks()
    module.fail_json(msg=checks_list)

    if has_different(checks_list, module):
        if module.params['state'] == "absent":
            if check_exists(checks_list, module.params['label']):
                exit(0)
                # delete_check(module, old_trigger)
        else:
            exit(0)

if __name__ == '__main__':
    main()
