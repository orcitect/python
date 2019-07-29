#!/usr/bin/env python
'''
This script ensures users belonging to the given LDAP group have
database access and revokes privileges for defunct users.
'''

from ldap3 import Server, Connection, Tls, SUBTREE
from ldap3.core.exceptions import LDAPCursorError
import pymysql.cursors
import ssl
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# sql cfg

pam_auth = "maxscale"
hostname = "%"
connection = pymysql.connect(user="root")

# ldap cfg

groups = ["prodsql", "prodsql-masked"]
uri = "ldaps://ldap.domain.com"
dn_usr = "ou=People,dc=domain,dc=com"
dn_grp = "dc=doamin,dc=com"


def ldap_lookup(entry):

    tls = Tls(version=ssl.PROTOCOL_TLSv1_1)
    server = Server(uri, tls=tls)

    with Connection(server) as conn:
        try:
            conn.search(dn_grp, "(&(cn={})(objectClass=posixGroup))".format(entry), search_scope=SUBTREE, attributes=['memberUid'])
            result = conn.entries[0].memberUid
            return result
        except (LDAPCursorError, IndexError):
            pass
        try:
            conn.search(dn_usr, "(&(uid={})(objectClass=person))".format(entry), search_scope=SUBTREE, attributes=['uidNumber'])
            result = conn.entries[0].uidNumber
            return result
        except IndexError:
            pass


def main():

    ldap = []

    for item in groups:
        data = ldap_lookup(item)
        try:
            ldap.extend(data)
        except TypeError:
            pass

    # SQL lookup

    with connection.cursor() as cursor:
        cursor.execute('SELECT user FROM mysql.user WHERE authentication_string=%s', (pam_auth,))
        sql_users = cursor.fetchall()
        sql = [data[0] for data in sql_users]

    # compare results

    sql_diff = [set(ldap) - set(sql)]
    ldap_diff = [set(sql) - set(ldap)]

    # no diff: exit

    if not (sql_diff or ldap_diff):
        log.info("LDAP & SQL users already in sync, exiting...")

    else:

        # SQL diff: create user

        if sql_diff:
            with connection.cursor() as cursor:
                for user in sql_diff:
                    cursor.execute('CREATE USER IF NOT EXISTS %s@%s IDENTIFIED VIA pam USING %s', (user, hostname, pam_auth,))
                    cursor.execute('GRANT SHOW DATABASES, SHOW VIEW, SELECT ON *.* TO %s@%s', (user, hostname,))
                log.info("Created SQL user for memberUid={}".format(ldap_lookup(user)))
            connection.commit()
            connection.close()

        # LDAP diff: drop user

        if ldap_diff:
            with connection.cursor() as cursor:
                for user in ldap_diff:
                    cursor.execute('DROP USER IF EXISTS %s@%s', (user, hostname,))
                    log.info("Dropped SQL user for memberUid={}".format(ldap_lookup(user)))
            connection.commit()
            connection.close()


if __name__ == '__main__':
    main()
