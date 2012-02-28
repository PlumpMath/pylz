#!/usr/bin/env python3


# stdlib
import sys
# local
import ints
import util


'''
Lempel-Ziv (LZ77 ???)

'''


###############################################################################


@util.coroutine
def encode(nxt, quiet=False):
    '''Produce [pointer][newbyte] bytes according to LempelZiv.
    
    Consume single bytes.
    
    When finished:
      Print a message to stderr. (Set quiet to True to disable)

    '''
    blocknum = 0
    table = {}
    buf = b''
    try:
        while True:
            # get a byte
            byte = yield
            if len(byte) != 1:
                raise ValueError('lz.encoder: got {}'.format(byte))
            buf += byte
            # check if it makes the current buffer new
            if buf not in table:
                # remember the new block
                blocknum += 1
                table[buf] = blocknum
                # encode the new block
                known, new = buf[:-1], buf[-1:]
                pfxptr = ints.tobytes(table[known] if len(known) else blocknum,
                                      length=ints.bytewidth(blocknum))
                # send encoded bytes
                nxt.send(pfxptr + new)
                # start over
                buf = b''
    finally:
        if not quiet:
            print('lz.encoder: {} blocks done'.format(blocknum),
                  file=sys.stderr)


###############################################################################

