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
    '''Compress a stream of bytes according to LempelZiv.

    Consume single bytes. Produce pointer-newbyte bytes.
    
    When finished:
      Send buffer as a lone prefix. (If any leftover)
      Print a message to stderr. (Set quiet to True to disable)

    Note1: The first block has no pointer.
    Note2: The last block may have no newbyte.

    '''
    table = {}
    blocknum = 0
    block = b''
    try:
        while True:
            # get a byte
            byte = yield
            if len(byte) != 1:
                raise ValueError('lz.encoder: got {} bytes in {}'.
                                 format(len(byte), byte))
            block += byte
            # check if the block is new; if so, compress it
            if block not in table:
                table[block] = blocknum
                known, new = block[:-1], block[-1:]
                pfxptr = ints.tobytes(table[known] if known else blocknum,
                                      length=ints.bytewidth(blocknum))
                nxt.send(pfxptr + new)
                # start over
                blocknum += 1
                block = b''
    finally:
        if block:
            nxt.send(ints.tobytes(table[block],
                                  length=ints.bytewidth(blocknum)))
        if not quiet:
            print('lz.encoder: {} blocks done'.format(blocknum),
                  file=sys.stderr)


###############################################################################


@util.coroutine
def decode(nxt, quiet=False):
    '''Decompress a stream of bytes compressed with "lz.encode".

    Consume single bytes. Produce decompressed bytes.
    
    When finished:
#      Send remaining uncompressed buffer.
      Print a message to stderr. (Set quiet to True to disable)

    '''
    table = {}
    blocknum = 0
    block = b''
    try:
        while True:
            # get a byte
            byte = yield
            if len(byte) != 1:
                raise ValueError('lz.decoder: got {} bytes in {}'.
                                 format(len(byte), byte))
            block += byte
            # check if the block is complete; if so decompress it
            width = ints.bytewidth(blocknum) + 1
            if len(block) == width:
                # split into prefix and new byte
                pfxptr, new = block[:-1], block[-1:]
                # expand it
                block = pfxptr and table[ints.frombytes(pfxptr)]
                pfx = ... if pfxptr in table else ...
                table[blocknum] = (pfxptr and table[pfxptr)]) + new
                if pfxptr != blocknum:
                    # lookup prefix in table
                # remember it
                table[pfxptr] = new
                pints.frombytes(pfxptr)
                table[] = ....
                table[block] = blocknum
                pfxptr = ints.tobytes(table[known] if known else blocknum,
                                      length=ints.bytewidth(blocknum))
                nxt.send(pfxptr + new)
                # start over
                blocknum += 1
                block = b''
    finally:
        if block:
            nxt.send(ints.tobytes(table[block],
                                  length=ints.bytewidth(blocknum)))
        if not quiet:
            print('lz.encoder: {} blocks done'.format(blocknum),
                  file=sys.stderr)


###############################################################################
