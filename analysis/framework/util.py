# -*- coding: utf-8 -*-

"""
Helpful utilities.
"""


__all__ = ["join_struct_arrays", "iter_chunks", "round_base", "partial_slices"]


import types

import six


def join_struct_arrays(*arrays):
    import numpy as np

    new_dtype = sum((a.dtype.descr for a in arrays), [])
    new_array = np.empty(len(arrays[0]), dtype=new_dtype)

    for a in arrays:
        for name in a.dtype.names:
            new_array[name] = a[name]

    return new_array

def iter_chunks(l, size):
    """
    Returns a generator containing chunks of *size* of a list, integer or generator *l*. A *size*
    smaller than 1 results in no chunking at all.
    """
    if isinstance(l, six.integer_types):
        l = six.range(l)

    if isinstance(l, types.GeneratorType):
        if size < 1:
            yield list(l)
        else:
            chunk = []
            for elem in l:
                if len(chunk) < size:
                    chunk.append(elem)
                else:
                    yield chunk
                    chunk = []
            if chunk:
                yield chunk

    else:
        if size < 1:
            yield l
        else:
            for i in six.range(0, len(l), size):
                yield l[i:i+size]


def round_base(num, base=1):
    """
    Returns a number *num* (*int* or *float*) rounded to an arbitrary *base*. Example:

    .. code-block:: python

       round_base(7, 3)   # => 6
       round_base(18, 5)  # => 20
       round_base(18., 5) # => 20. (float)
    """
    return num.__class__(base * round(float(num) / base))


def partial_slices(l, fractions, size=1):
    """
    Creates partial indexes for a sequence *l* according to *fractions* which should sum up to 1 or
    less. When *fractions* is an integer, it is interpreted as a number of equally sized fractions.
    *size* controls the portions of elements that will be treated en bloc. Example:

    .. code-block:: python

       partial_slices(60, [0.5, 0.25])
       # -> "[(0, 30), (30, 45)]"

       partial_slices(60, 3 * [1./3])
       # -> "[(0, 20), (20, 40), (40, 60)]"

       partial_slices(60, 3 * [1./3], size=12)
       # -> "[(0, 24), (24, 36), (36, 60)]"

    Note that *size* must always be an integer divider of the length of the passed sequence.
    """
    # check size
    n = l if not hasattr(l, "__len__") else len(l)
    if n % size != 0:
        raise ValueError("bad size {}, must be an integer divider of {}".format(size, n))

    # check fractions
    if isinstance(fractions, six.integer_types):
        fractions = fractions * [1. / fractions]
    if sum(fractions) > 1:
        raise ValueError("bad fractions, sum should be less the 1")
    if any(fraction < 0 for fraction in fractions):
        raise ValueError("bad fractions, should all be positive")

    slices = []

    rest = 0.
    for f in fractions:
        # the start index is the end index of the last iteration or 0
        start = 0 if len(slices) == 0 else slices[-1][1]

        # the end index is more complicated
        chunk = f * n + rest
        closest = round_base(chunk, size)
        rest = chunk - closest
        end = start + int(closest)

        slices.append((start, end))

    return slices
