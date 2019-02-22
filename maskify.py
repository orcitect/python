#!/usr/bin/env python3

import re

regex = re.compile(r'[0-9]+?')


def maskify(cc):

    cc = cc.replace('-', '').replace(' ', '')

    if len(cc) <= 5:
        return cc
    else:
        new_cc = cc[0] + regex.sub('#', cc[1:-4]) + cc[-4:]
        return new_cc


if __name__ == '__main__':
    #maskify('123456')
    for _ in range(10000000):
        maskify('A12B2D3E4F586H7K')
