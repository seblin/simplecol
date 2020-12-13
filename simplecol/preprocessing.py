from collections.abc import Mapping
from fnmatch import translate
from io import IOBase
from locale import strxfrm
import re

__all__ = [
    "prepare", "read_lines", "get_column",
    "get_filtered", "get_unique", "get_sorted"
]

def prepare(values, colidx=None, pattern=None, unique=False, sort=False):
    if isinstance(values, IOBase):
        values = read_lines(values)
    if colidx is not None:
        values = get_column(values, colidx)
    if pattern is not None:
        values = get_filtered(values, pattern)
    if unique and not isinstance(values, Mapping):
        values = get_unique(values)
    if sort:
        values = get_sorted(values)
    return values

def read_lines(stream):
    return [line.rstrip() for line in stream]

def get_column(lines, index):
    return [line.split()[index] for line in lines]

def get_unique(values):
    try:
        # Python preserves the order when keys
        # are added to a dict. Can not use a set,
        # since its ordering is undefined.
        result = list(dict.fromkeys(values))
    except TypeError:
        # Fallback for unhashable types. Should be
        # be a relatively rare case, so no further
        # optimizations are made for this.
        result = []
        for value in values:
            if value not in result:
                result.append(value)
    return result

def get_sorted(values):
    try:
        # Locale-dependent sorting.
        result = sorted(values, key=strxfrm)
    except TypeError:
        # Fallback to "default" sorting when dealing
        # with non-string values (e.g. numbers).
        result = sorted(values)
    return set_result(values, result)

def get_filtered(values, pattern):
    if not isinstance(pattern, re.Pattern):
        pattern = re.compile(translate(pattern), re.IGNORECASE)
    result = filter(pattern.fullmatch, values)
    return set_result(values, result)

def set_result(values, result):
    if isinstance(values, Mapping):
        return {key: values[key] for key in result}
    return list(result)
