# -*- coding: utf-8 -*-

"""
Helpful utilities.
"""


__all__ = ["join_struct_arrays"]


def join_struct_arrays(*arrays):
    import numpy as np

    new_dtype = sum((a.dtype.descr for a in arrays), [])
    new_array = np.empty(len(arrays[0]), dtype=new_dtype)

    for a in arrays:
        for name in a.dtype.names:
            new_array[name] = a[name]

    return new_array
