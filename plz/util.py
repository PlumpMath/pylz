'''
A generator is a function that produces a sequence of results instead of a
single value.

Don't mix production and consumption of values in a generator, as in
"inval = yield outval", instead stick to either a generator "yield outval"
or a coroutine "inval = yield".

'''


def coroutine(f):
    '''Prime the generator f with send(None) when it is called.

    A coroutine generally consumes a sequence of values. Coroutines are not
    related to iteration. Use a source-loop to feed values into a pipeline of
    coroutines with send(), and a sink-coroutine to deal with the results.

    '''
    def prime(*args, **kwargs):
        c = f(*args, **kwargs)
        c.send(None)
        return c
    return prime
