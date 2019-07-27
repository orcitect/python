#!/usr/bin/env python
'''
This script maintains maxscale's masking and dbfwfilters by
examining privileges based on LDAP group membership.

It applies column masking and fw rules that prevents execution
of functions on sensitive fields such as passwords etc.
'''

from ldap3 import Server, Connection, Tls, SUBTREE
import json
import subprocess
import tempfile
import os
import jinja2
import ssl
import logging


logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(__name__)


fw_tmpl = """\
rule deny_concat match function concat
{% for user in users %}
users {{ user }}@% match all rules deny_concat
{%- endfor %}
""" + '\n'


fw_filter = '/etc/maxscale.modules.d/firewall.txt'
mask_filter = '/etc/maxscale.modules.d/masking.json'
mask_backup = mask_filter + '.bak'
group = 'prodsql-masked'
uri = 'ldaps://ldap.domain.com'
dn = 'dc=domain,dc=com'


def ldap_group(name):

    with Connection(Server(uri, tls=Tls(version=ssl.PROTOCOL_TLSv1_1))) as cnx:
        cnx.search(dn, '(&(cn={})(objectClass=posixGroup))'.format(name), search_scope=SUBTREE, attributes=['memberUid', 'objectclass'])
        return json.loads(cnx.entries[0].entry_to_json())


def main():

    ldap = ldap_group(group)

    with open(mask_filter, 'r') as fin:
        fltr = json.load(fin)

    if not fltr['rules'][0]['applies_to'] == ldap['attributes']['memberUid']:
        log.info('Changes found, updating filter...')

        for n in range(0, len(fltr['rules'])):
            fltr['rules'][n]['applies_to'] = ldap

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as fout:
            json.dump(fltr, fout)

        os.rename(mask_filter, mask_backup)
        os.rename(fout.name, mask_filter)
        os.chmod(mask_filter, 0o644)

        subprocess.call([
            'maxctrl',
            'call',
            'command',
            'masking',
            'reload',
            'masking'
        ])
        log.info('Masking filter updated!')

        # update firewall

        jinja2.Template(fw_tmpl).stream(users=ldap['attributes']['memberUid']).dump(fw_filter)
        subprocess.call(['maxctrl', 'call', 'command', 'dbfwfilter', 'rules/reload', 'firewall'])
        log.info('Firewall filter updated!')

    else:
        log.info('Filter and LDAP contain the same data. Exiting...')


if __name__ == '__main__':
    main()
