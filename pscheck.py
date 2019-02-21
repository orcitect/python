#!/usr/bin/env python3

import psutil


def pscheck(seekitem):
    plist = psutil.process_iter()
    strl = " ".join(str(x) for x in plist)
    if seekitem in strl:
        print("requested process is running")


if __name__ == '__main__':
    pscheck("System")
