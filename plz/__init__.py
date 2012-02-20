#!/usr/bin/python3

# stdlib
import sys
# local
import util


###############################################################################


def source(fd, nxt):
    '''Pump single bytes from file-like fd through coroutine pipeline nxt.'''
    while True:
        nxt.send(fd.read(1))


@util.coroutine
def sink(fd):
    '''Recieve bytes and write them to the file-like fd.'''
    while True:
        x = yield
        fd.write(x)


###############################################################################


__all__ = []


if __name__ == '__main__':
    if '-c' in sys.argv:
        s = open(filename, mode='rb')
        t = open(filename, mode='wb')
    else:
        s = sys.stdin.buffer
        t = sys.stdout.buffer
    # start actual source and sink
    source(s, sink(t))
