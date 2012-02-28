#!/usr/bin/env python3


# stdlib
import sys


'''
Most of the advice about generators and coroutines in this file are ideas from
David Beazley's "A Curious Course on Coroutines and Concurrency"
<http://www.dabeaz.com/coroutines/>.

A generator is a function that produces a sequence of results instead of a
single value.

Don't mix production and consumption of values in a generator, as in
"inval = yield outval", instead stick to either a generator "yield outval"
or a coroutine "inval = yield".

'''


###############################################################################


def coroutine(f):
    '''Prime the coroutine f with send(None) when it is called.

    A coroutine generally consumes a sequence of values. Coroutines are not
    related to iteration. Use a source-loop to feed values into a pipeline of
    coroutines with send(), and a sink-coroutine to deal with the results.

    '''
    def prime(*args, **kwargs):
        c = f(*args, **kwargs)
        c.send(None)
        return c
    return prime


###############################################################################


def filesource(fd, nxt, close=True, quiet=False):
    '''Pump single bytes from file-like fd through coroutine pipeline nxt.
    
    When finished:
      Print a message to stderr. (Set quiet to True to disable)
      Close the coroutine pipeline. (Set close to False to disable)

    '''
    byt = fd.read(1)
    while byt:
        nxt.send(byt)
        byt = fd.read(1)
    # wrap up
    if not quiet:
        print('util.filesource: eof reached', file=sys.stderr)
    if close:
        nxt.close()


@coroutine
def filesink(fd, close=False, quiet=False):
    '''Recieve bytes and write them to the file-like fd.
    
    When finished:
      Print a message to stderr. (Set quiet to True to disable)
      (Set close to True to enable) Close the file-like fd.

    '''
    try:
        while True:
            x = yield
            fd.write(x)
    finally:
        if not quiet:
            print('util.filesink: done', file=sys.stderr)
        if close:
            fd.close()


###############################################################################

