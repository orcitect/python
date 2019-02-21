""" sha2-hash your password """

import uuid
import hashlib

#print(hashlib.algorithms_available)
#print(hashlib.algorithms_guaranteed)

def hash_password(password):
    """hash"""
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

def check_password(hashed_password, user_password):
    """return"""
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

new_pass = raw_input('Please enter a password: ')
hashed_password = hash_password(new_pass)

print 'Hashed password: ' + hashed_password
