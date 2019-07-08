# Ansible module for NodePing
---

## Usage

```
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
```