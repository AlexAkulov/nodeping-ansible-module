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
        required: false
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
        aliases: ["desc"]
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
        default: 5
        type: str
        choices: [ 1, 3, 5, 15, 30, 60, 240, 360, 1800, 3600 ]
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
    rechecks:
        description:
            - Rechecks help avoid unnecessary notifications. For most services we recommend "high"
        required: false
        default: 2
        type: int
        choices:
            - 0
            - 2
            - 5
            - 7
            - 10
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
    - name: nodeping ckecks must be created
      nodeping-check-http:
        name: "{{ item.name }}"
        url: "{{ item.url }}"
        token: "{{ lookup('env','NODEPING_TOKEN') }}"
        notifications:
          myslack:
            delay: 0
            schedule: Days
        state: present
      with_items:
        - name: check ya.ru
          url: https://ya.ru
        - name: check google.com
          url: https://google.com

- hosts: localhost
  tasks:
    - nodeping-check-http:
        name: example.com
        state: absent
'''

from ansible.module_utils.basic import AnsibleModule
import sys
sys.path.append('./')
from nodeping_api import get_checks as nodeping_get_checks
from nodeping_api import delete_checks as nodeping_delete_checks
from nodeping_api import create_check as nodeping_create_check
from nodeping_api import update_checks as nodeping_update_checks
from nodeping_api import get_contacts as nodeping_get_contacts

def trim_suffix(s, suffix):
    if s.endswith(suffix):
        return s[:-len(suffix)]
    return s

def get_check_by_label(checks_list, label):
    for key, value in checks_list.items():
        if value.get('label', "") == label:
            return value
    return {}

def notifications_converter(contacts_list, module):
    result = []
    contacts = module.params['notifications']
    if not contacts:
        return result

    for contact in contacts:
        for key, value in contacts_list.items():
            if contact['name'] != value['name']:
                continue
            for contact_id, v in value.get('addresses', {}).items():
                result.append({
                    contact_id: {
                        "delay": value.get('delay', 0),
                        "schedule": value.get('shedule', 'Days')
                        }})
    return result

def create_check(contacts, module):
    loc = "NAM"
    result = nodeping_create_check.http_check(
        module.params['token'],
        module.params['url'],
        label=module.params['label'],
        ipv6=module.params['force_ipv6_resolution'],
        follow=module.params['follow_redirects'],
        interval=module.params['frequency'],
        enabled=module.params['enabled'],
        # runlocations=,
        threshold=module.params['temeout'],
        sens=module.params['rechecks'],
        notifications=contacts
    )
    if 'error' in result:
        module.fail_json(msg=result)
    module.exit_json(changed=True, msg="created id: %s"%result.get('_id'))

def get_diff(contacts, check, module):

    if any(check):
        before = {
            "enable": check['enable'],
            "follow": check['parameters']['follow'],
            "ipv6": check['parameters']['ipv6'],
            "sens": check['parameters']['sens'],
            "target": trim_suffix(check['parameters']['target'], '/'),
            "threshold": check['parameters']['threshold'],
            "public": check['public'],
            "interval": check['interval'],
            "description": check.get('description', " "),
            "notifications": check['notifications'],
            "type": check['type']
        }
    after = {
        "enable": "active" if module.params['enabled'] else "inactive",
        "follow": module.params['follow_redirects'],
        "ipv6": module.params['force_ipv6_resolution'],
        "sens": module.params['rechecks'],
        "target": trim_suffix(module.params['url'], '/'),
        "threshold": module.params['timeout'],
        "public": module.params['public_results'],
        "interval": module.params['frequency'],
        "description": module.params['description'],
        "notifications": contacts,
        "type": "HTTP"
    }
    diff = {
        'before': before,
        'after': after,
#       'before_header': '%s (content)' % dest,
#       'after_header': '%s (content)' % dest
    }
    return diff

def main():
    module = AnsibleModule(
        argument_spec=dict(
            label=dict(type='str', aliases=['name'], required=False),
            token=dict(type='str', required=True),
            enabled=dict(type='bool', required=False, default=True),
            state=dict(type='str', required=False, default='present', choices=['present', 'absent']),
            description=dict(type='str', aliases=['desc'], required=False, default=" "),
            public_results=dict(type='bool', aliases=['public'], required=False, default=False),
            region=dict(type='str', required=False, default='default', choices=['default', 'north america', 'europe', 'east asia/oceania', 'latin america', 'world wide']),
            frequency=dict(type='int', aliases=['interval'], required=False, default=5, choices=[1, 3, 5, 15, 30, 60, 240, 360, 1800, 3600]),
            url=dict(type='str', required=True),
            force_ipv6_resolution=dict(type='bool', aliases=['ipv6'], required=False, default=False),
            follow_redirects=dict(type='bool', aliases=['follow'], required=False, default=True),
            timeout=dict(type='int', required=False, default=5),
            rechecks=dict(type='int', required=False, default=2, choices=[0, 2, 5, 7, 10]),
            notifications=dict(type='list', required=False, default=[])
        )
    )
    checks_list = nodeping_get_checks.GetChecks(module.params['token']).all_checks()
    contacts_list = nodeping_get_contacts.get_all(module.params['token'])
    contacts = notifications_converter(contacts_list, module)

    # module.fail_json(msg=contacts_list)

    check = get_check_by_label(checks_list, module.params['label'])

    if module.params['state'] == 'absent':
        if any(check):
            if not module.check_mode:
                nodeping_delete_checks.remove(module.params['token'], check.get('_id'))
            module.exit_json(changed=True)
        module.exit_json(changed=False)

    if any(check):
        # update
        diff = get_diff(contacts, check, module)
        if diff['before'].__eq__(diff['after']):
            module.exit_json(changed=False)

        if module.check_mode:
            module.exit_json(changed=True, diff=diff)

        result = nodeping_update_checks.update(
            module.params['token'],
            check.get('_id'), diff['after'])
        if 'errors' in result:
            module.fail_json(msg=result)
        module.exit_json(changed=True, msg=result, diff=diff)


    # create
    if module.check_mode:
        module.exit_json(changed=True)
    create_check(contacts, module)

if __name__ == '__main__':
    main()
