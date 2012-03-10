#!/usr/bin/env python3


# stdlib
import os
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
            num = yield
            block += bytes([num])
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


@cr.composedin(cr.trickle, None)
@cr.coroutine
def decode(nxt, quiet=False):
    '''Decompress a stream of bytes compressed by "lz.encode".

    Consume bytes. Produce decompressed bytes.

    When finished:
###      Send buffer as a lone prefix. (If any leftover)
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


def readfrom(args):
    return args.file or sys.stdin.buffer


def writeto(parser, args, suf):
    def shortername():
        if args.file.name.endswith(suf):
            return args.file.name[:-len(suf)]
        else:
            parser.error('{}: unknown suffix -- ignored'.
                         format(args.file.name))
    def longername():
        if not args.file.name.endswith(suf):
            return args.file.name + suf
        else:
            parser.error('{} already has {} suffix -- unchanged'.
                         format(args.file.name, suf))
    def afile():
        fn = shortername() if args.decompress else longername()
        if not os.path.exists(fn):
            return open(fn, mode='wb')
        else:
            parser.error('{} already exists; not overwritten'.format(fn))
    # -- in --
    return sys.stdout.buffer if args.stdout else afile()


DESC = '''Compress or decompress data with Lempel-Ziv. Given no file or given
-, read from standard input and write to standard output. This program does
not perform error correction (don't entrust your important data to it yet).'''


if __name__ == '__main__':

    # parse arguments
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

    # read stdin implies write stdout
    if ns.file is None:
        ns.stdout = True

    print(ns)

    # get source and sink file objects
    s = readfrom(ns)
    t = writeto(ap, ns, '.plz')

    # start pipeline
    print('s', s)
    print('t', t)
    q = not ns.verbose
    proc = decode if ns.decompress else encode
    cr.filesource(s, proc(cr.filesink(t, quiet=q), quiet=q), quiet=q)


###############################################################################
## EOF
