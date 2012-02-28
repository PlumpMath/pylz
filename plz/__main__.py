#!/usr/bin/env python3


# stdlib
import sys
# local
import lz
import util


###############################################################################


if __name__ == '__main__':
    if '-c' in sys.argv:
        s = sys.stdin.buffer
        t = sys.stdout.buffer
    elif sys.argv[1:]:
        s = open(sys.argv[1], mode='rb')
        t = open(sys.argv[2], mode='wb')
    else:
        print('USAGE: python3 ......................... [ -c ] [ name-in name-out ]')
    # start actual source and sink
    util.filesource(s, lz.encode(util.filesink(t)))


###############################################################################

