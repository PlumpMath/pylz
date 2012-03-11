#!/usr/bin/env python3


# stdlib
import sys
import functools


'''Coroutine support utilities.

"A generator is a function that produces a sequence of results instead of a
single value [dabeaz 16]."

A coroutine generally consumes a sequence of values [dabeaz 31]. "Coroutines
are not related to iteration [dabeaz 33]." Use a source-loop to feed values
into a pipeline of coroutines with send() [dabeaz 36], and a sink-coroutine to
deal with the results [dabeaz 37].

Don't mix production and consumption of values in a generator, as in
"inval = yield outval" [dabeaz 33]. Instead stick to either a generator
"yield outval" or a coroutine "inval = yield".

[Cited "dabeaz"]
    David Beazley "A Curious Course on Coroutines and Concurrency"
    Slides: http://www.dabeaz.com/coroutines/Coroutines.pdf
    About: http://www.dabeaz.com/coroutines/

'''


###############################################################################
## Support Functions


def filesource(fd, nxt, chunk=512, close=True, quiet=False):
    '''Function to pump chunks from file-like fd into coroutine-pipeline nxt.

    fd:
        Must be opened with a binary mode that allows reading.
        Should have a buffering strategy (such as the Python default).

    When finished:
        Print a message to stderr. (Set quiet to True to disable)
        Close the coroutine pipeline. (Set close to False to disable)

    '''
    def read():
        return fd.read(chunk)
    # send chunks
    byt = read()
    while byt:
        nxt.send(byt)
        byt = read()
    # wrap up
    if not quiet:
        print('cr.filesource: eof reached', file=sys.stderr)
    if close:
        nxt.close()


def compose(*coroutines, splitargs=None, wraps=None):
    '''Function to produce the composition of coroutines (a premade pipeline).

    For example:
        compose(f, g, h) makes a pipeline like f->g->h() where f and g each
        take a coroutine as their first argument.

    splitargs:
        Optional. A function which takes arguments given to the composition and
        returns a sequence (length n) of tuples (length 2) containing the args
        and kwargs objects to be given to the individual coroutines. A 'None'
        in an args object will be replaced with the next coroutine in the
        pipeline.

        If splitargs is omitted, arguments given to the composition are
        given to the last coroutine in the pipeline, and it is assumed
        that each other coroutine takes the next one as its only
        argument.

    wraps:
        Optional. The index of the coroutine argument which has the docstring
        which the resultant composition should also have.

    '''
    if splitargs is None:
        def splitargs(*args, **kwargs):
            '''Default splitargs.

            Each coroutine gets one argument (the next step in the pipeline)
            except the final coroutine (which gets whatever arguments were
            passed to composition).

            '''
            argseq = [([None], {}) for cr in coroutines]
            argseq[-1] = (args, kwargs)
            return argseq

    def composition(*args, **kwargs):
        '''Initialize and compose the given coroutines.'''
        # split up arguments
        argseq = splitargs(*args, **kwargs)
        # initialize the final coroutine
        args, kwargs = argseq[-1]
        nxt = coroutines[-1](*args, **kwargs)
        # initialize the other coroutines in reverse, each wrapping its next
        for cr, (args, kwargs) in reversed(list(zip(coroutines[:-1],
                                                    argseq[:-1]))):
            args[args.index(None)] = nxt
            nxt = cr(*args, **kwargs)
        return nxt

    if wraps is not None:
        composition = functools.wraps(coroutines[wraps])(composition)

    return composition


###############################################################################
## Decorators


def coroutine(f):
    '''Decorator to prime the generator f with send(None) when it is called.

    [dabeaz 27]

    '''
    @functools.wraps(f)
    def prime(*args, **kwargs):
        c = f(*args, **kwargs)
        c.send(None)
        return c

    return prime


def composedin(*coroutines, splitargs=None):
    '''Decorator to compose the coroutine f in a pipeline of others.

    The decorated function will replace 'None' in the arguments to this
    decorator in the final composition.

    For example:

        @composedin(f, None, h)
        @coroutine
        def g(nxt):
            pass # (some coroutine code here)

        Creates a pipeline like f->g->h() and names it g.

    See "compose" in this module for more information.

    '''
    crs = list(coroutines) or [None]

    def do_composition(f):
        wrapped = crs.index(None)
        crs[wrapped] = f
        return compose(*crs, splitargs=splitargs, wraps=wrapped)

    return do_composition


###############################################################################
## Exceptions


class UnsentError(Exception):
    '''Exception for when a coroutine was closed but still had data to send.'''
    pass


###############################################################################
## Utility Coroutines


@coroutine
def printer():
    '''Coroutine. Print whatever is sent.

    [dabeaz 38]

    '''
    while True:
        x = yield
        print(x)


@coroutine
def filesink(fd, close=False, quiet=False):
    '''Coroutine. Consume bytes objects. Write them to the file-like fd.

    fd:
        Must be opened with a binary mode that allows writing.
        Should have a buffering strategy (such as the Python default).

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
            print('cr.filesink: done', file=sys.stderr)
        if close:
            fd.close()


@coroutine
def trickle(nxt):
    '''Coroutine. Consume sequences. Send single elements to coroutine nxt.'''
    try:
        while True:
            seq = yield
            for i, e in enumerate(seq):
                nxt.send(e)
    finally:
        rest = seq[i + 1:]
        if rest:
            raise UnsentError(rest)


###############################################################################
## EOF
