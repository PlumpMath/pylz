#!/usr/bin/env python3


# stdlib
import sys
import argparse
# local
import cr
import ints


'''Lempel-Ziv encoder and decoder with Python3 coroutines.

This is a byte-level implementation of Lempel-Ziv in which each block contains
some number of bytes to reference its known-prefix and exactly one new-byte.

- Blocks refer to their known-prefix with absolute addressing.
- The first block has no reference to a prefix.
- The last block may or may not have a new-byte.

'''


###############################################################################
## Encoder


@cr.composedin(cr.trickle, None)
@cr.coroutine
def encode(nxt, quiet=False):
    '''Compress a stream of bytes according to LempelZiv.

    Consume bytes. Produce pointer-newbyte bytes.

    When finished:
      Send buffer as a lone prefix. (If any leftover)
      Print a message to stderr. (Set quiet to True to disable)

    '''
    table = {}
    blocknum = 0
    block = b''
    try:
        while True:
            # extend the buffer by one byte
            byte = yield
            block += byte
            # compress the block if it is unfamiliar
            if block not in table:
                table[block] = blocknum
                known, new = block[:-1], block[-1:]
                pfxptr = ints.tobytes(table[known] if known else blocknum,
                                      length=ints.bytewidth(blocknum))
                nxt.send(pfxptr + new)
                # start again
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
## Decoder


@cr.coroutine
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
                #pfx = ... if pfxptr in table else ...
                #table[blocknum] = (pfxptr and table[pfxptr)]) + new
                #if pfxptr != blocknum:
                    # lookup prefix in table
                # remember it
                table[pfxptr] = new
                pints.frombytes(pfxptr)
                #table[] = ....
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
## Main


DESC = '''Compress or decompress data with Lempel-Ziv. Given no file or given
-, read from standard input and write to standard output. This program does
not perform error correction (don't entrust your important data to it yet).'''


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=DESC)
    ap.add_argument('-c', '--stdout', action='store_true',
                    help='write to standard output instead of a file')
    ap.add_argument('-d', '--decompress', action='store_true',
                    help='decompress data instead')
    ap.add_argument('-v', '--verbose', action='store_false',
                    help='print status messages to standard error')
    ap.add_argument('file', nargs='?', type=argparse.FileType('rb'),
                    help='file to read')
    ns = ap.parse_args()
    #
    print(ns)
    print()
    # compress or decompress? <-- "-d" option
    # read stdin or a file?   <-- presence or absence of file argument
    # write stdout or a file? <-- "-c" option or no "-c" option and a file
    #
    # a. stdin to stdout "lz -c -"      or "lz -c"
    # b. file  to stdout "lz -c file"
    # c. stdin to file   "lz -"         or "lz"    <- gzip assumes "-c" in this case
    # d. file  to file   "lz file"
    #
    # file is None OR "-c" option is given --> write to standard out

    # where do we read from?
    if ns.file is None:
        # from stdin
        s = sys.stdin.buffer
    else:
        # from a file
        s = ns.file

    # where do we write to?
    if ns.file is None or ns.stdout:
        # to stdout
        t = sys.stdout.buffer
    else:
        # to a file
        #
        if ns.decompress and ns.file.name[-3:] != '.lz'

    # don't decompress a file with an unknown suffix
    if ns.decompress and ns.file and ns.file.name[-3:] != '.lz':
        pass

#
#     if ns.stdout:
#         t = sys.stdout.buffer
#     else:
#         fn = ns.file.name + ('.lz' if
#         t = open(
#
#
#     if '-c' in sys.argv:
#         s = sys.stdin.buffer
#         t = sys.stdout.buffer
#     elif sys.argv[1:]:
#         s = open(sys.argv[1], mode='rb')
#         t = open(sys.argv[2], mode='wb')
#     else:
#         print(    # start actual source and sink
#     cr.filesource(s, lz.encode(util.filesink(t)))


###############################################################################
## EOF
