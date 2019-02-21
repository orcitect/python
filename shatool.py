""" jarfiles shell-python conversion """

import hashlib
import sys

BLOCKSIZE = 1024*64

with open(sys.argv[1], 'rb', buffering=0):
    