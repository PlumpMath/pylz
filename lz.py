#!/usr/bin/env python3


# stdlib
import os
import sys
import argparse
import itertools
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
    table = {} # map known chunks to blockids
    try:
        for blockid in itertools.count():
            nums = []
            chunk = None
            # accumulate an unfamiliar chunk
            while chunk in table or chunk is None:
                nums.append((yield))
                chunk = bytes(nums)
            # remember the chunk
            table[chunk] = blockid
            # compress the chunk to a block
            prefix, newbyte = chunk[:-1], chunk[-1:]
            pointer = table[prefix] if prefix else blockid
            pointerb = ints.tobytes(pointer, length=ints.bytewidth(blockid))
            # send the block
            nxt.send(pointerb + newbyte)
    finally:
        if nums:
            pointer = table[bytes(nums)]
            pointerb = ints.tobytes(pointer, length=ints.bytewidth(blockid))
            # send partial block
            nxt.send(pointerb)
        if not quiet:
            ct = blockid + (0.5 if nums else 0)
            print('lz.encoder: {} blocks done'.format(ct), file=sys.stderr)


###############################################################################
## Decoder


@cr.composedin(cr.trickle, None)
@cr.coroutine
def decode(nxt, quiet=False):
    '''Decompress a stream of bytes compressed by "lz.encode".

    Consume bytes. Produce decompressed bytes.

    When finished:
      Treat remaining bytes as a lone prefix. (If any leftover)
      Print a message to stderr. (Set quiet to True to disable)

    '''
    table = {} # map blockids to known chunks
    try:
        for blockid in itertools.count():
            nums = []
            # accumulate the next block
            for _ in range(ints.bytewidth(blockid) + 1):
                nums.append((yield))
            block = bytes(nums)
            # decompress the block to a chunk
            pointerb, newbyte = block[:-1], block[-1:]
            pointer = ints.frombytes(pointerb)
            prefix = b'' if pointer == blockid else table[pointer]
            # remember the chunk
            table[blockid] = prefix + newbyte
            # send the chunk
            nxt.send(table[blockid])
    finally:
        if nums:
            pointerb = bytes(nums)
            pointer = ints.frombytes(pointerb)
            nxt.send(table[pointer])
        if not quiet:
            ct = blockid + (0.5 if nums else 0)
            print('lz.decoder: {} blocks done'.format(ct), file=sys.stderr)


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
