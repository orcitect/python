"""
    usage: python filehash.py <filename>
    compat: 2.7, 3.4
    todo: checksum generation + verification
"""

import sys
import hashlib

BUFFER = 65536  # read in 64kb chunks

with open(sys.argv[1], 'rb', buffering=0) as filename:
    while True:
        DATA = filename.read(BUFFER)
        if not DATA:
            break
        sha1hash = hashlib.sha1(DATA)
        sha1hashed = sha1hash.hexdigest()
        #HASH.update(DATA)
        #HASH(DATA)

#print 'sha1sum:', "{0}".format(HASH.hexdigest()))
#print 'Same:', (DATA == DATA2)

print(sha1hashed)
