#!/usr/bin/env python3


# stdlib
import sys
import time
# local
import cr


###############################################################################
## Support Functions


def _raise(e):
    '''Allow raise in expressions.'''
    raise e


###############################################################################
## Progress


class Progress:
    '''A context manager & iterator to indicate progress at intervals.

    foos = range(12)                    # a list of jobs to do
    with Progress(12, timeout=5) as p:
        for afoo in foos:
            time.sleep(1)               # work on afoo
            p.next()                    # indicate progress

    Alternatively, you can use the iterator interface.

    foos = range(12)
    with Progress(12, timeout=5) as p:
        for afoo, _ in zip(foos, p):
            time.sleep(1)

    '''

    def __init__(self, total, timeout=0, callback=None):
        # item count
        self.current = None
        self.total = total
        # elapsed time
        self.begun = None
        # callback
        self.prev = None
        self.timeout = timeout
        if callback is None:
            self.callback = (lambda current, total, elapsed:
                             print('Completed {} of {} items; {} elapsed.'.
                                   format(current, total,
                                          format_time(1000 * elapsed))))
        else:
            self.callback = callback

    def __enter__(self):
        # local
        now = time.time()
        # item count
        self.current = 0
        # elapsed time
        self.begun = now
        # callback
        self.prev = now
        self.callback(0, self.total, 0)
        return self

    def next(self, did=1):
        # local
        now = time.time()
        # item count
        self.current += did
        # determine if we're done
        if self.current >= self.total:
            self.next = lambda *args: _raise(StopIteration)
        # callback
        if (now - self.prev) > self.timeout or self.current >= self.total:
            self.prev = now
            return self.callback(self.current, self.total, now - self.begun)

    def __exit__(self, e_type, e_value, e_traceback):
        # try to make final call to callback
        self.timeout = 0
        if self.current < self.total:
            self.next(self.total - self.current)
        return False # this cm doesn't care about exceptions

    # be an iterator too

    def __next__(self):
        return self.next()

    def __iter__(self):
        return self


###############################################################################
## Utilities


def bar(message=None, width=10):
    '''Make a callback for Progress which prints a bar like [##---].'''
    message = '' if message is None else (message + ' ')
    def fn(current, total, elapsed):
        blocks = int(float(current) / total * width)
        sys.stdout.write('\r{}[{}{}] {:{w}}/{} {}{}'.format(
            message,
            blocks * '#',
            (width - blocks) * '-',
            current,
            total,
            format_time(1000 * elapsed),
            '\n' if current == total else '',
            w=len(str(total)),
            ))
        sys.stdout.flush()
    return fn


def format_time(milliseconds):
    '''Make a human-readable string from the given number of milliseconds.

    >>> format_time(3723004)
    '01:02:03.004'
    >>> format_time(123004)
    '02:03.004'
    >>> format_time(3004)
    '03.004'
    >>> format_time(4)
    '004'
    >>> format_time(0)
    '000'
    '''
    ms = int(milliseconds)
    h = ms // 3600000
    m = ms % 3600000 // 60000
    s = ms % 3600000 % 60000 // 1000
    ms = ms % 3600000 % 60000 % 1000
    #         ms/hr,    ms/min, ms/s
    return ('{:02}:'.format(h) if h else '') + \
           ('{:02}:'.format(m) if h or m else '') + \
           ('{:02}.'.format(s) if h or m or s else '') + \
           '{:03}'.format(ms)


@cr.coroutine
def coroutine(nxt, total, timeout=1, callback=None, count=lambda x: 1):
    '''Coroutine. Send anything consumed to nxt. Indicate progress.

    total:
        The maximum number of things expected. When the progress of the things
        consumed reaches total, close.

    timeout:
    callback:
        See the Progress class.

    count:
        Optional. A function which takes a consumed thing and determines how
        much progress it represents. By default consumed things count as one.

    '''
    with Progress(total, timeout, callback) as p:
        while True:
            thing = yield
            p.next(did=count(thing))
            nxt.send(thing)


###############################################################################
## EOF
