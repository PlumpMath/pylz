#!/usr/bin/env python3


#stdlib
from math import log, ceil


###############################################################################


def bitwidth(val):
    return ceil(log(val + 1, 2))


assert bitwidth(0b0) == 0
assert bitwidth(0b1) == 1
assert bitwidth(0b10) == 2
assert bitwidth(0b11) == 2
assert bitwidth(0b101) == 3
assert bitwidth(0b1011) == 4
assert bitwidth(0b11010) == 5
assert bitwidth(0b110100101) == 9
assert bitwidth(0b1010110100) == 10


###############################################################################


def bytewidth(val):
    return ceil(bitwidth(val) / 8)


assert bytewidth(0b0) == 0
assert bytewidth(0b1) == 1
assert bytewidth(0b10) == 1
assert bytewidth(0b11) == 1
assert bytewidth(0b101) == 1
assert bytewidth(0b10110111) == 1
assert bytewidth(0b101101010) == 2
assert bytewidth(0b1010111010000010) == 2
assert bytewidth(0b1010111010001000010) == 3


###############################################################################


def tobytes(val, length=None):
    '''Convert an integer to a bytes of the minimum (or specified) length.'''
    w = bytewidth(val)
    if length is None:
        pass
    elif length < w:
            raise ValueError('{} is less than width of {}, {}'.
                             format(length, val, w))
    else:
        w = length
    return bytes(255 & (val >> 8 * i) for i in reversed(range(w)))


assert tobytes(0) == b''
assert tobytes(0, 2) == b'\x00\x00'
assert tobytes(97   ) == b'a'
assert tobytes(97, 1) == b'a'
assert tobytes(97, 2) == b'\x00a'
assert tobytes(97, 3) == b'\x00\x00a'
assert tobytes(495891539314) == b'super'


###############################################################################


def frombytes(byt):
    '''Convert bytes to the corresponding integer.'''
    n = 0
    for i, b in enumerate(reversed(list(byt))):
        n |= b << 8 * i
    return n


assert frombytes(b'') == 0
assert frombytes(b'\x00') == 0
assert frombytes(b'\x01') == 1
assert frombytes(b'\x02') == 2
assert frombytes(b'\x02\x80') == 640
assert frombytes(b'\x00\x02\x80') == 640
assert frombytes(tobytes(987654321)) == 987654321


###############################################################################

